package com.crusty.lessons;

import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;
import android.view.View;
import android.widget.RemoteViews;
import java.util.Calendar;

public class WidgetUpdater {

    private static final int[] ROWS = {
            R.id.r0, R.id.r1, R.id.r2, R.id.r3,
            R.id.r4, R.id.r5, R.id.r6, R.id.r7
    };

    public static void updateAll(Context c) {
        AppWidgetManager m = AppWidgetManager.getInstance(c);
        push(c, m, m.getAppWidgetIds(new ComponentName(c, WidgetSmall.class)), 0);
        push(c, m, m.getAppWidgetIds(new ComponentName(c, WidgetMedium.class)), 1);
        push(c, m, m.getAppWidgetIds(new ComponentName(c, WidgetLarge.class)), 2);
    }

    // size: 0 = маленький, 1 = средний, 2 = большой
    public static void push(Context c, AppWidgetManager m, int[] ids, int size) {
        if (ids == null || ids.length == 0) return;
        Profile p = new Store(c).getActive();
        for (int id : ids) {
            m.updateAppWidget(id, build(c, p, size));
        }
    }

    private static RemoteViews build(Context c, Profile p, int size) {
        Schedule.Status st = Schedule.status(p, Calendar.getInstance());
        int layout = size == 0 ? R.layout.widget_small
                : size == 1 ? R.layout.widget_medium
                : R.layout.widget_large;

        RemoteViews v = new RemoteViews(c.getPackageName(), layout);
        int bg = "liquid".equals(p.widgetStyle) ? R.drawable.bg_liquid : R.drawable.bg_glass;
        v.setInt(R.id.root, "setBackgroundResource", bg);
        v.setTextViewText(R.id.tvTimer, st.timer);

        if (size >= 1) {
            v.setTextViewText(R.id.tvName, p.name);
            v.setTextViewText(R.id.tvNext, st.next);
        }

        if (size == 2) {
            v.setProgressBar(R.id.pb, 100, st.progress, false);
            for (int i = 0; i < ROWS.length; i++) {
                if (st.activeDay && i < st.lessons.size()) {
                    Schedule.Lesson l = st.lessons.get(i);
                    v.setViewVisibility(ROWS[i], View.VISIBLE);
                    v.setTextViewText(ROWS[i],
                            l.number + ".  " + Schedule.fmt(l.start) + " – " + Schedule.fmt(l.end));
                    v.setInt(ROWS[i], "setTextColor",
                            i == st.currentIndex ? 0xFFA5D6A7 : 0xFFE8F5E9);
                } else {
                    v.setViewVisibility(ROWS[i], View.GONE);
                }
            }
        }
        return v;
    }
}
