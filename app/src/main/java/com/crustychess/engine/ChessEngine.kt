package com.crustychess.engine

/**
 * UCI engine adapter contract.
 *
 * Next implementation step:
 * 1. Bundle a compatible Stockfish Android binary for supported ABIs.
 * 2. Start it with ProcessBuilder.
 * 3. Send `uci`, `isready`, `position fen ...`, and `go depth ...`.
 * 4. Parse `info ... multipv ... score ... pv ...` and `bestmove`.
 */
data class EngineLine(
    val rank: Int,
    val scoreCp: Int?,
    val mateIn: Int?,
    val principalVariationUci: List<String>
)

interface ChessEngine {
    suspend fun start()
    suspend fun analyse(fen: String, depth: Int, multiPv: Int): List<EngineLine>
    suspend fun stop()
}
