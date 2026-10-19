package com.crustychess

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.crustychess.overlay.FloatingPanelService

private val Ink = Color(0xFF07100B)
private val Deep = Color(0xFF0B1710)
private val Glass = Color(0xCC15271B)
private val Green = Color(0xFFB5F59A)
private val Lime = Color(0xFF76D66D)
private val TextMain = Color(0xFFF0F6EF)
private val TextMuted = Color(0xFF9DAFA0)

class MainActivity : ComponentActivity() {
    private var overlayAllowed by mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        overlayAllowed = Settings.canDrawOverlays(this)
        setContent {
            MaterialTheme(
                colorScheme = darkColorScheme(
                    primary = Green,
                    onPrimary = Ink,
                    secondary = Lime,
                    background = Ink,
                    surface = Glass,
                    onBackground = TextMain,
                    onSurface = TextMain,
                    outline = Color(0xFF35513B)
                ),
                typography = Typography(
                    headlineLarge = MaterialTheme.typography.headlineLarge.copy(
                        fontFamily = FontFamily.SansSerif, fontWeight = FontWeight.Black, letterSpacing = (-1.4).sp
                    ),
                    titleLarge = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
                    labelSmall = MaterialTheme.typography.labelSmall.copy(letterSpacing = 1.4.sp)
                )
            ) {
                HomeScreen(
                    overlayPermission = overlayAllowed,
                    onEnableOverlay = { requestOverlayPermission() },
                    onOpenChannel = {
                        startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://t.me/CrustySearch")))
                    },
                    onOpenOverlay = {
                        if (Settings.canDrawOverlays(this)) {
                            startService(Intent(this, FloatingPanelService::class.java))
                        } else requestOverlayPermission()
                    }
                )
            }
        }
    }

    override fun onResume() {
        super.onResume()
        overlayAllowed = Settings.canDrawOverlays(this)
    }

    private fun requestOverlayPermission() {
        if (!Settings.canDrawOverlays(this)) {
            startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName")))
        } else startService(Intent(this, FloatingPanelService::class.java))
    }
}

@Composable
private fun HomeScreen(
    overlayPermission: Boolean,
    onEnableOverlay: () -> Unit,
    onOpenChannel: () -> Unit,
    onOpenOverlay: () -> Unit
) {
    Box(
        modifier = Modifier.fillMaxSize().background(
            Brush.verticalGradient(listOf(Color(0xFF102418), Ink, Color(0xFF050906)))
        )
    ) {
        // Subtle ambient glass glow.
        Box(Modifier.align(Alignment.TopEnd).padding(top = 30.dp, end = 10.dp).size(180.dp)
            .clip(CircleShape).background(Brush.radialGradient(listOf(Color(0x333ED45B), Color.Transparent))))
        Column(
            Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 26.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text("CRUSTY / CHESS", color = Green, style = MaterialTheme.typography.labelSmall)
                    Spacer(Modifier.height(5.dp))
                    Text("See the board.\nThink clearly.", color = TextMain, style = MaterialTheme.typography.headlineLarge, lineHeight = 39.sp)
                }
                Box(Modifier.size(58.dp).clip(RoundedCornerShape(20.dp))
                    .background(Brush.linearGradient(listOf(Color(0xFFB5F59A), Color(0xFF3C9D56))))
                    .border(1.dp, Color(0x88FFFFFF), RoundedCornerShape(20.dp)), contentAlignment = Alignment.Center) {
                    Text("♞", color = Ink, fontSize = 34.sp)
                }
            }
            Text("LOCAL ANDROID COMPANION  ·  V1.0", color = TextMuted, style = MaterialTheme.typography.labelSmall)

            GlassCard {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                        Text("FLOATING PANEL", color = Green, style = MaterialTheme.typography.labelSmall)
                        Text("Keep CrustyChess on top", style = MaterialTheme.typography.titleLarge)
                        Text("Move the glass panel anywhere over your screen.", color = TextMuted, style = MaterialTheme.typography.bodyMedium)
                    }
                    Box(Modifier.size(42.dp).clip(CircleShape).background(Color(0x223FE16B)), contentAlignment = Alignment.Center) {
                        Text("↗", color = Green, fontSize = 25.sp)
                    }
                }
                Spacer(Modifier.height(12.dp))
                StatusPill(text = if (overlayPermission) "OVERLAY PERMISSION ENABLED" else "PERMISSION REQUIRED", active = overlayPermission)
                Button(
                    onClick = if (overlayPermission) onOpenOverlay else onEnableOverlay,
                    modifier = Modifier.fillMaxWidth().height(52.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Green, contentColor = Ink)
                ) { Text(if (overlayPermission) "OPEN FLOATING PANEL  ↗" else "ENABLE FLOATING WINDOW", fontWeight = FontWeight.Bold) }
            }

            GlassCard {
                Text("V1 SCOPE", color = Green, style = MaterialTheme.typography.labelSmall)
                Spacer(Modifier.height(6.dp))
                FeatureRow("01", "Glass floating window", "Draggable panel with Start, Stop and Close controls.")
                FeatureRow("02", "Green visual system", "Dark emerald surfaces, soft gradients and restrained lime accents.")
                FeatureRow("03", "Recognition status", "This build is the UI/overlay foundation; live screen recognition and Stockfish are not wired into Start yet.")
            }

            GlassCard {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text("PROJECT CHANNEL", color = Green, style = MaterialTheme.typography.labelSmall)
                        Text("@CrustySearch", style = MaterialTheme.typography.titleLarge)
                        Text("The project channel. Subscription is not server-verified in this build.", color = TextMuted, style = MaterialTheme.typography.bodySmall)
                    }
                    OutlinedButton(onClick = onOpenChannel, shape = RoundedCornerShape(14.dp)) { Text("OPEN ↗") }
                }
            }
            Text("CRUSTYCHESS  /  BUILD 1.0.0 · ANDROID", color = Color(0xFF66796A), style = MaterialTheme.typography.labelSmall)
        }
    }
}

@Composable
private fun GlassCard(content: @Composable ColumnScope.() -> Unit) {
    Column(
        modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(24.dp))
            .background(Brush.linearGradient(listOf(Color(0xDD1A3021), Color(0xB30B160F))))
            .border(1.dp, Brush.linearGradient(listOf(Color(0x667FBA87), Color(0x22FFFFFF))), RoundedCornerShape(24.dp))
            .padding(18.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        content = content
    )
}

@Composable
private fun StatusPill(text: String, active: Boolean) {
    Row(
        modifier = Modifier.clip(CircleShape).background(if (active) Color(0x223FE16B) else Color(0x22E5B85C))
            .padding(horizontal = 11.dp, vertical = 7.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(7.dp)
    ) {
        Box(Modifier.size(6.dp).clip(CircleShape).background(if (active) Green else Color(0xFFE5B85C)))
        Text(text, color = if (active) Green else Color(0xFFE5C77E), style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun FeatureRow(number: String, title: String, description: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 5.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(number, color = Green, style = MaterialTheme.typography.labelMedium)
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
            Text(title, fontWeight = FontWeight.SemiBold)
            Text(description, color = TextMuted, style = MaterialTheme.typography.bodySmall, lineHeight = 18.sp)
        }
    }
}
