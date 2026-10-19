package com.crustychess.onboarding

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

/**
 * First-run checklist. Subscription is not trusted based on a local checkbox:
 * the app must ask the backend to verify Telegram membership.
 */
@Composable
fun SetupGuide(
    subscriptionVerified: Boolean,
    onOpenChannel: () -> Unit,
    onRecheckSubscription: () -> Unit,
    onOpenChessComInstructions: () -> Unit,
    onStartCalibration: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        Text("CrustyChess setup", style = MaterialTheme.typography.headlineMedium)
        Text("Complete setup to unlock local position analysis.")

        Card {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("1. Join @CrustySearch", style = MaterialTheme.typography.titleMedium)
                Text(
                    if (subscriptionVerified) "Membership verified."
                    else "Join the project channel. CrustyChess will verify membership with its server."
                )
                Button(onClick = onOpenChannel, modifier = Modifier.fillMaxWidth()) {
                    Text("Open Telegram channel")
                }
                OutlinedButton(onClick = onRecheckSubscription, modifier = Modifier.fillMaxWidth()) {
                    Text("Check subscription")
                }
            }
        }

        Card {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("2. Set the Chess.com board theme", style = MaterialTheme.typography.titleMedium)
                Text(
                    "Open Chess.com → Settings → Themes → Board, then choose the green board theme. " +
                    "Return here when finished. The exact labels can vary by app version."
                )
                OutlinedButton(onClick = onOpenChessComInstructions, modifier = Modifier.fillMaxWidth()) {
                    Text("Show board setup instructions")
                }
            }
        }

        Card {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("3. Calibrate board recognition", style = MaterialTheme.typography.titleMedium)
                Text(
                    "Place a full board on screen with all 64 squares visible. Avoid menus, animations, " +
                    "coordinates covering squares, and floating elements over the board."
                )
                Button(
                    onClick = onStartCalibration,
                    enabled = subscriptionVerified,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Calibrate board")
                }
                if (!subscriptionVerified) {
                    Text(
                        "Analysis remains locked until the server verifies channel membership.",
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
    }
}
