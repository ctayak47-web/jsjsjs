package com.crustychess.recognition

import org.opencv.core.Mat
import org.opencv.core.Rect
import org.opencv.imgproc.Imgproc
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sqrt

data class BoardGeometry(
    val bounds: Rect,
    val squareSize: Double,
    val confidence: Float,
    val lightRgb: Triple<Double, Double, Double>,
    val darkRgb: Triple<Double, Double, Double>
)

data class PiecePrediction(
    /** FEN piece symbol, null means empty or unknown. */
    val fenSymbol: Char?,
    val confidence: Float
)

data class RecognizedBoard(
    val fen: String?,
    val confidence: Float,
    val needsConfirmation: Boolean,
    val reason: String,
    val geometry: BoardGeometry? = null,
    /** 64 cells in FEN order: rank 8 to rank 1, file a to h. */
    val cells: List<PiecePrediction> = emptyList()
)

fun interface PieceClassifier {
    fun classify(squareRgb: Mat): PiecePrediction?
}

/**
 * DPI-independent board locator. It operates on captured frame pixels rather
 * than dp coordinates, so different Android display densities do not change
 * the geometry math.
 *
 * This locates the board by its alternating green/cream squares. Pair it with
 * ChessComGreenPieceClassifier for the matching Chess.com piece set. The
 * template classifier is intended for this exact theme and should be calibrated
 * against real captures before being treated as production-accurate.
 */
class GreenBoardRecognizer(
    private val pieceClassifier: PieceClassifier,
    private val minGeometryConfidence: Float = 0.76f,
    private val minPieceConfidence: Float = 0.76f
) {
    fun recognize(frameRgb: Mat, sideToMove: Char? = null): RecognizedBoard {
        if (frameRgb.empty() || frameRgb.cols() < 240 || frameRgb.rows() < 240) {
            return unknown("Captured frame is too small.")
        }
        val geometry = locateBoard(frameRgb)
            ?: return unknown("Green board not found. Keep all 64 squares visible and retry.")

        if (geometry.confidence < minGeometryConfidence) {
            return RecognizedBoard(null, geometry.confidence, true,
                "Board location is uncertain; adjust the screen and retry.", geometry)
        }

        val square = geometry.squareSize.toInt()
        val inset = max(2, (square * 0.12).toInt())
        val cells = ArrayList<PiecePrediction>(64)

        for (rank in 0 until 8) {
            for (file in 0 until 8) {
                val x = geometry.bounds.x + file * square + inset
                val y = geometry.bounds.y + rank * square + inset
                val side = max(1, square - 2 * inset)
                if (x < 0 || y < 0 || x + side > frameRgb.cols() || y + side > frameRgb.rows()) {
                    cells += PiecePrediction(null, 0f)
                    continue
                }
                val roi = Rect(x, y, side, side)
                val crop = Mat(frameRgb, roi)
                val prediction = try { pieceClassifier.classify(crop) }
                    finally { crop.release() }
                cells += prediction ?: PiecePrediction(null, 0f)
            }
        }

        val uncertain = cells.count { it.confidence < minPieceConfidence }
        if (uncertain > 0) {
            return RecognizedBoard(null, min(geometry.confidence, cells.minOf { it.confidence }),
                true, "$uncertain squares need review. No position will be treated as certain.",
                geometry, cells)
        }

        val placement = cells.chunked(8).joinToString("/") { row ->
            buildString {
                var empty = 0
                for (cell in row) {
                    val piece = cell.fenSymbol
                    if (piece == null) empty++ else {
                        if (empty > 0) append(empty)
                        empty = 0
                        append(piece)
                    }
                }
                if (empty > 0) append(empty)
            }
        }

        val symbols = cells.mapNotNull { it.fenSymbol }
        val whiteKings = symbols.count { it == 'K' }
        val blackKings = symbols.count { it == 'k' }
        val whitePawns = symbols.count { it == 'P' }
        val blackPawns = symbols.count { it == 'p' }
        val whitePieces = symbols.count { it.isUpperCase() }
        val blackPieces = symbols.count { it.isLowerCase() }
        val backRankPawn = (0 until 8).any { file ->
            cells[file].fenSymbol == 'P' || cells[file].fenSymbol == 'p' ||
                cells[56 + file].fenSymbol == 'P' || cells[56 + file].fenSymbol == 'p'
        }
        val invalidReason = when {
            whiteKings != 1 || blackKings != 1 -> "Position check failed: expected exactly one king of each color."
            whitePawns > 8 || blackPawns > 8 -> "Position check failed: more than eight pawns of one color."
            whitePieces > 16 || blackPieces > 16 -> "Position check failed: too many pieces of one color."
            backRankPawn -> "Position check failed: a pawn appears on the first or eighth rank."
            else -> null
        }
        if (invalidReason != null) {
            return RecognizedBoard(
                null,
                min(geometry.confidence, cells.minOf { it.confidence }),
                true,
                "$invalidReason Review the board recognition before continuing.",
                geometry,
                cells
            )
        }

        if (sideToMove != 'w' && sideToMove != 'b') {
            return RecognizedBoard("$placement ? - - 0 1",
                min(geometry.confidence, cells.minOf { it.confidence }), true,
                "Confirm whose turn it is and the position's rule state.", geometry, cells)
        }
        return RecognizedBoard("$placement $sideToMove - - 0 1",
            min(geometry.confidence, cells.minOf { it.confidence }), true,
            "Confirm castling rights and en-passant state before analysis.", geometry, cells)
    }



    private data class Candidate(val x: Int, val y: Int, val cell: Int, val score: Float)

    private fun locateBoard(frame: Mat): BoardGeometry? {
        // Downsample once. All search happens in capture-image pixels, never dp.
        val maxDimension = 480.0
        val scale = min(1.0, maxDimension / max(frame.cols(), frame.rows()))
        val small = Mat()
        try {
            Imgproc.resize(
                frame, small,
                org.opencv.core.Size(
                    max(1.0, frame.cols() * scale),
                    max(1.0, frame.rows() * scale)
                ),
                0.0, 0.0, Imgproc.INTER_AREA
            )
            val sampler = PixelSampler(small)
            val minDimension = min(small.cols(), small.rows())
            val minCell = max(12, (minDimension * 0.52 / 8.0).toInt())
            val maxCell = (minDimension * 0.98 / 8.0).toInt()
            val coarse = mutableListOf<Candidate>()
            var cell = minCell

            // Coarse scan finds likely checkerboard regions cheaply.
            while (cell <= maxCell) {
                val side = cell * 8
                if (side <= small.cols() && side <= small.rows()) {
                    val positionStep = max(4, cell / 2)
                    var y = 0
                    while (y + side <= small.rows()) {
                        var x = 0
                        while (x + side <= small.cols()) {
                            val score = scoreCandidate(sampler, x, y, cell)
                            if (score >= 0.55f) coarse += Candidate(x, y, cell, score)
                            x += positionStep
                        }
                        y += positionStep
                    }
                }
                cell += max(2, (cell * 0.04).toInt())
            }
            if (coarse.isEmpty()) return null

            // Center-only scores cannot distinguish an offset inside a square.
            // Refine the strongest coarse candidates by checking actual grid edges.
            val refined = mutableListOf<Candidate>()
            for (candidate in coarse.sortedByDescending { it.score }.take(6)) {
                val radius = max(4, candidate.cell / 2)
                val posStep = max(1, candidate.cell / 12)
                val minX = max(0, candidate.x - radius)
                val maxX = min(small.cols() - candidate.cell * 8, candidate.x + radius)
                val minY = max(0, candidate.y - radius)
                val maxY = min(small.rows() - candidate.cell * 8, candidate.y + radius)
                val minCandidateCell = max(12, candidate.cell - 2)
                val maxCandidateCell = min(maxCell, candidate.cell + 2)
                for (candidateCell in minCandidateCell..maxCandidateCell) {
                    val candidateSide = candidateCell * 8
                    if (candidateSide > small.cols() || candidateSide > small.rows()) continue
                    var y = minY
                    while (y <= maxY && y + candidateSide <= small.rows()) {
                        var x = minX
                        while (x <= maxX && x + candidateSide <= small.cols()) {
                            val score = scoreCandidateFine(sampler, x, y, candidateCell)
                            refined += Candidate(x, y, candidateCell, score)
                            x += posStep
                        }
                        y += posStep
                    }
                }
            }
            val best = refined.maxByOrNull { it.score } ?: coarse.maxByOrNull { it.score } ?: return null
            val side = best.cell * 8
            val light = sampler.mean(best.x + best.cell / 2, best.y + best.cell / 2, max(2, best.cell / 5))
            val dark = sampler.mean(
                best.x + best.cell + best.cell / 2,
                best.y + best.cell / 2,
                max(2, best.cell / 5)
            )
            return BoardGeometry(
                Rect(
                    (best.x / scale).toInt(),
                    (best.y / scale).toInt(),
                    (side / scale).toInt(),
                    (side / scale).toInt()
                ),
                best.cell / scale,
                best.score,
                light,
                dark
            )
        } finally {
            small.release()
        }
    }


    private fun scoreCandidate(image: PixelSampler, x: Int, y: Int, cell: Int): Float {
        val samples = sampleCenters(image, x, y, cell)
        val alternating = alternatingScore(samples)
        val green = samples.count { isGreen(it) } / 64.0
        val greenScore = if (green in 0.22..0.78) 1.0 - abs(green - 0.5) else 0.0
        return (0.72 * alternating + 0.28 * greenScore).toFloat()
            .takeIf { alternating > 0.82 && greenScore > 0.4 } ?: 0f
    }

    private fun scoreCandidateFine(image: PixelSampler, x: Int, y: Int, cell: Int): Float {
        val samples = sampleCenters(image, x, y, cell)
        val alternating = alternatingScore(samples)
        val green = samples.count { isGreen(it) } / 64.0
        val greenScore = if (green in 0.22..0.78) 1.0 - abs(green - 0.5) else 0.0

        val boundaryDistances = ArrayList<Double>(112)
        val offset = max(1, cell / 12)
        for (row in 0 until 8) {
            val cy = y + row * cell + cell / 2
            for (col in 1 until 8) {
                val bx = x + col * cell
                boundaryDistances += distance(
                    image.mean(bx - offset, cy, 1),
                    image.mean(bx + offset, cy, 1)
                )
            }
        }
        for (col in 0 until 8) {
            val cx = x + col * cell + cell / 2
            for (row in 1 until 8) {
                val by = y + row * cell
                boundaryDistances += distance(
                    image.mean(cx, by - offset, 1),
                    image.mean(cx, by + offset, 1)
                )
            }
        }
        val centerDistances = ArrayList<Double>(112)
        for (row in 0 until 8) for (col in 0 until 8) {
            val index = row * 8 + col
            if (col < 7) centerDistances += distance(samples[index], samples[index + 1])
            if (row < 7) centerDistances += distance(samples[index], samples[index + 8])
        }
        val boundaryScore = (
            boundaryDistances.average() / (centerDistances.average() + 1e-6)
        ).coerceIn(0.0, 1.0)
        return (0.55 * alternating + 0.20 * greenScore + 0.25 * boundaryScore).toFloat()
    }

    private fun sampleCenters(image: PixelSampler, x: Int, y: Int, cell: Int)
        : List<Triple<Double, Double, Double>> {
        val result = ArrayList<Triple<Double, Double, Double>>(64)
        for (row in 0 until 8) for (col in 0 until 8) {
            result += image.mean(
                x + col * cell + cell / 2,
                y + row * cell + cell / 2,
                max(2, cell / 5)
            )
        }
        return result
    }

    private fun alternatingScore(samples: List<Triple<Double, Double, Double>>): Double {
        var alternating = 0
        var compared = 0
        for (row in 0 until 8) for (col in 0 until 8) {
            val index = row * 8 + col
            if (col < 7) {
                if (distance(samples[index], samples[index + 1]) > 24.0) alternating++
                compared++
            }
            if (row < 7) {
                if (distance(samples[index], samples[index + 8]) > 24.0) alternating++
                compared++
            }
        }
        return alternating.toDouble() / max(1, compared)
    }

    private class PixelSampler(mat: Mat) {
        private val width = mat.cols()
        private val height = mat.rows()
        private val channels = mat.channels()
        private val pixels = ByteArray(width * height * channels)

        init {
            mat.get(0, 0, pixels)
        }

        fun mean(cx: Int, cy: Int, radius: Int): Triple<Double, Double, Double> {
            val left = (cx - radius).coerceIn(0, width - 1)
            val top = (cy - radius).coerceIn(0, height - 1)
            val right = (cx + radius).coerceIn(left + 1, width)
            val bottom = (cy + radius).coerceIn(top + 1, height)
            var red = 0.0
            var green = 0.0
            var blue = 0.0
            var count = 0
            for (py in top until bottom) for (px in left until right) {
                val base = (py * width + px) * channels
                red += pixels[base].toInt() and 0xff
                if (channels > 1) green += pixels[base + 1].toInt() and 0xff
                if (channels > 2) blue += pixels[base + 2].toInt() and 0xff
                count++
            }
            val divisor = max(1, count).toDouble()
            return Triple(red / divisor, green / divisor, blue / divisor)
        }
    }

    private fun isGreen(c: Triple<Double, Double, Double>) =
        c.second > c.first * 1.04 && c.second > c.third * 0.92

    private fun distance(a: Triple<Double, Double, Double>, b: Triple<Double, Double, Double>): Double {
        val r = a.first - b.first
        val g = a.second - b.second
        val bl = a.third - b.third
        return sqrt(r * r + g * g + bl * bl)
    }

    private fun unknown(message: String) = RecognizedBoard(null, 0f, true, message)
}
