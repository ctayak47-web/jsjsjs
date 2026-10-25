package com.crusty.lessons;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.ColorStateList;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import java.util.Calendar;
import java.util.List;

public class MainActivity extends Activity {

    private Store store;
    private Theme th;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        store = new Store(this);
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 0);
        }
        startForegroundService(new Intent(this, LessonService.class));
    }

    @Override
    protected void onResume() {
        super.onResume();
        render();
    }

    private void render() {
        th = Theme.of(store.getTheme());
        Profile active = store.getActive();
        List<Profile> profiles = store.getProfiles();
        Schedule.Status st = Schedule.status(active, Calendar.getInstance());

        ScrollView sv = new ScrollView(this);
        sv.setBackground(th.background());
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = Ui.dp(this, 20);
        root.setPadding(pad, Ui.dp(this, 48), pad, Ui.dp(this, 28));
        sv.addView(root);

        root.addView(Ui.text(this, "CrustyLessons", 28, th.text, true));
        root.addView(Ui.text(this, "Профиль: " + active.name, 14, th.textDim, false));

        // Карточка статуса
        LinearLayout card = Ui.column(this, th.glassCard(this), 20);
        card.addView(Ui.text(this, st.timer, 26, th.accent, true));
        card.addView(Ui.text(this, st.next, 15, th.text, false));
        ProgressBar pb = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        pb.setMax(100);
        pb.setProgress(st.progress);
        pb.setProgressTintList(ColorStateList.valueOf(th.accent));
        pb.setProgressBackgroundTintList(ColorStateList.valueOf(th.button));
        LinearLayout.LayoutParams pbLp = Ui.fill();
        pbLp.topMargin = Ui.dp(this, 12);
        card.addView(pb, pbLp);
        root.addView(card, Ui.withTop(this, 18));

        // Список уроков на сегодня
        if (st.activeDay) {
            LinearLayout list = Ui.column(this, th.glassCard(this), 16);
            for (int i = 0; i < st.lessons.size(); i++) {
                Schedule.Lesson l = st.lessons.get(i);
                boolean cur = i == st.currentIndex;
                String line = "Урок " + l.number + "   " + Schedule.fmt(l.start)
                        + " – " + Schedule.fmt(l.end);
                list.addView(Ui.text(this, line, 15, cur ? th.accent : th.text, cur));
            }
            root.addView(list, Ui.withTop(this, 14));
        }

        // Профили
        root.addView(Ui.text(this, "Профили", 13, th.textDim, false), Ui.withTop(this, 22));
        HorizontalScrollView hs = new HorizontalScrollView(this);
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        for (Profile p : profiles) {
            Button b = Ui.pill(this, th, p.name, p.id.equals(active.id));
            b.setOnClickListener(select(p.id));
            row.addView(b, Ui.gap(this));
        }
        hs.addView(row);
        root.addView(hs, Ui.withTop(this, 8));

        // Действия
        LinearLayout actions = new LinearLayout(this);
        actions.setOrientation(LinearLayout.HORIZONTAL);
        Button edit = Ui.pill(this, th, "Изменить", false);
        edit.setOnClickListener(open(EditActivity.class, active.id));
        Button add = Ui.pill(this, th, "Новый", false);
        add.setOnClickListener(open(EditActivity.class, null));
        Button settings = Ui.pill(this, th, "Настройки", false);
        settings.setOnClickListener(open(SettingsActivity.class, null));
        actions.addView(edit, Ui.gap(this));
        actions.addView(add, Ui.gap(this));
        actions.addView(settings, Ui.gap(this));
        root.addView(actions, Ui.withTop(this, 14));

        // Подпись
        root.addView(Ui.text(this, "Создатель @swatlolz", 12, th.textDim, false),
                Ui.withTop(this, 32));
        root.addView(Ui.text(this, "Канал проекта @CrustySearch", 12, th.textDim, false));

        setContentView(sv);
    }

    private View.OnClickListener select(final String id) {
        return new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                store.setActiveId(id);
                WidgetUpdater.updateAll(MainActivity.this);
                render();
            }
        };
    }

    private View.OnClickListener open(final Class<?> cls, final String id) {
        return new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(MainActivity.this, cls);
                if (id != null) i.putExtra("id", id);
                startActivity(i);
            }
        };
    }
}
