package com.crusty.lessons;

import android.content.Context;
import android.graphics.drawable.GradientDrawable;

public class Theme {
    public final int bgTop, bgBottom, card, cardStroke, accent, onAccent, text, textDim, button;

    private Theme(int bgTop, int bgBottom, int card, int cardStroke, int accent,
                  int onAccent, int text, int textDim, int button) {
        this.bgTop = bgTop;
        this.bgBottom = bgBottom;
        this.card = card;
        this.cardStroke = cardStroke;
        this.accent = accent;
        this.onAccent = onAccent;
        this.text = text;
        this.textDim = textDim;
        this.button = button;
    }

    public static Theme of(String name) {
        switch (name) {
            case "graphite":
                return new Theme(0xFF1A1E1F, 0xFF0C0F10, 0x1FFFFFFF, 0x40FFFFFF,
                        0xFFB8E0C4, 0xFF0C0F10, 0xFFF2F4F3, 0xFF9AA5A0, 0x1AFFFFFF);
            case "mint":
                return new Theme(0xFFEAF5EE, 0xFFCFE8D8, 0x66FFFFFF, 0x99FFFFFF,
                        0xFF1F6B47, 0xFFFFFFFF, 0xFF0F2A1C, 0xFF4F6B5B, 0x40FFFFFF);
            default:
                return new Theme(0xFF0B3D2E, 0xFF06201A, 0x26FFFFFF, 0x4DFFFFFF,
                        0xFFA5D6A7, 0xFF06201A, 0xFFE8F5E9, 0xFF9CC5AE, 0x2EFFFFFF);
        }
    }

    public GradientDrawable background() {
        return new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                new int[]{bgTop, bgBottom});
    }

    public GradientDrawable glassCard(Context c) {
        GradientDrawable g = new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[]{card, 0x0DFFFFFF});
        g.setCornerRadius(Ui.dp(c, 24));
        g.setStroke(Ui.dp(c, 1), cardStroke);
        return g;
    }
}
