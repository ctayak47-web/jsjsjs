package com.crusty.lessons;

import android.content.Context;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.text.InputType;
import android.util.TypedValue;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class Ui {

    public static int dp(Context c, int v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v,
                c.getResources().getDisplayMetrics());
    }

    public static TextView text(Context c, String s, int sp, int color, boolean bold) {
        TextView t = new TextView(c);
        t.setText(s);
        t.setTextSize(sp);
        t.setTextColor(color);
        if (bold) t.setTypeface(Typeface.DEFAULT_BOLD);
        t.setPadding(0, dp(c, 3), 0, dp(c, 3));
        return t;
    }

    public static LinearLayout.LayoutParams fill() {
        return new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
    }

    public static LinearLayout.LayoutParams withTop(Context c, int topDp) {
        LinearLayout.LayoutParams lp = fill();
        lp.topMargin = dp(c, topDp);
        return lp;
    }

    public static LinearLayout.LayoutParams gap(Context c) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.rightMargin = dp(c, 8);
        return lp;
    }

    public static LinearLayout column(Context c, GradientDrawable bg, int padDp) {
        LinearLayout l = new LinearLayout(c);
        l.setOrientation(LinearLayout.VERTICAL);
        l.setBackground(bg);
        int p = dp(c, padDp);
        l.setPadding(p, p, p, p);
        return l;
    }

    public static GradientDrawable pillBg(Context c, Theme th, boolean selected) {
        GradientDrawable g = new GradientDrawable();
        g.setCornerRadius(dp(c, 24));
        g.setColor(selected ? th.accent : th.button);
        g.setStroke(dp(c, 1), th.cardStroke);
        return g;
    }

    public static Button pill(Context c, Theme th, String label, boolean selected) {
        Button b = new Button(c);
        b.setText(label);
        b.setAllCaps(false);
        b.setTextColor(selected ? th.onAccent : th.text);
        b.setBackground(pillBg(c, th, selected));
        return b;
    }

    public static void restyle(Context c, Button b, Theme th, boolean selected) {
        b.setTextColor(selected ? th.onAccent : th.text);
        b.setBackground(pillBg(c, th, selected));
    }

    public static EditText input(Context c, Theme th, String value, boolean numeric) {
        EditText e = new EditText(c);
        e.setText(value);
        e.setSingleLine(true);
        e.setTextColor(th.text);
        e.setHintTextColor(th.textDim);
        e.setBackground(pillBg(c, th, false));
        e.setPadding(dp(c, 16), dp(c, 12), dp(c, 16), dp(c, 12));
        if (numeric) e.setInputType(InputType.TYPE_CLASS_NUMBER);
        LinearLayout.LayoutParams lp = withTop(c, 6);
        e.setLayoutParams(lp);
        return e;
    }
}
