package com.crusty.lessons;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import java.util.List;

public class EditActivity extends Activity {

    private static final String[] DAYS = {"Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"};

    private Store store;
    private Theme th;
    private Profile p;
    private boolean isNew;
    private EditText etName, etStart, etCount, etLesson, etBreaks;
    private final CheckBox[] dayBoxes = new CheckBox[7];
    private String style;
    private Button btnGlass, btnLiquid;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        store = new Store(this);
        th = Theme.of(store.getTheme());
        String id = getIntent().getStringExtra("id");
        isNew = (id == null);
        p = new Profile();
        if (!isNew) {
            for (Profile x : store.getProfiles()) if (x.id.equals(id)) p = x;
        }
        style = p.widgetStyle;
        build();
    }

    private void build() {
        ScrollView sv = new ScrollView(this);
        sv.setBackground(th.background());
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = Ui.dp(this, 20);
        root.setPadding(pad, Ui.dp(this, 48), pad, Ui.dp(this, 28));
        sv.addView(root);
        setContentView(sv);

        root.addView(Ui.text(this, isNew ? "Новый профиль" : "Редактирование", 26, th.text, true));

        root.addView(label("Название"));
        etName = Ui.input(this, th, p.name, false);
        root.addView(etName);

        root.addView(label("Начало первого урока (ЧЧ:ММ)"));
        etStart = Ui.input(this, th, Schedule.fmt(p.startMin), false);
        root.addView(etStart);

        root.addView(label("Количество уроков (1–10)"));
        etCount = Ui.input(this, th, String.valueOf(p.lessonCount), true);
        root.addView(etCount);

        root.addView(label("Длина урока, минут (10–180)"));
        etLesson = Ui.input(this, th, String.valueOf(p.lessonMin), true);
        root.addView(etLesson);

        root.addView(label("Перемены через запятую, минут"));
        etBreaks = Ui.input(this, th, joinBreaks(p.breaks), false);
        root.addView(etBreaks);

        root.addView(label("Учебные дни"));
        LinearLayout dayRow = new LinearLayout(this);
        dayRow.setOrientation(LinearLayout.HORIZONTAL);
        for (int i = 0; i < 7; i++) {
            CheckBox cb = new CheckBox(this);
            cb.setText(DAYS[i]);
            cb.setTextColor(th.text);
            cb.setChecked((p.days & (1 << i)) != 0);
            dayBoxes[i] = cb;
            dayRow.addView(cb, new LinearLayout.LayoutParams(
                    0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        }
        root.addView(dayRow, Ui.fill());

        root.addView(label("Стиль виджета"));
        LinearLayout styleRow = new LinearLayout(this);
        styleRow.setOrientation(LinearLayout.HORIZONTAL);
        btnGlass = Ui.pill(this, th, "Стекло", "glass".equals(style));
        btnLiquid = Ui.pill(this, th, "Жидкое", "liquid".equals(style));
        btnGlass.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { style = "glass"; refreshStyle(); }
        });
        btnLiquid.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { style = "liquid"; refreshStyle(); }
        });
        styleRow.addView(btnGlass, Ui.gap(this));
        styleRow.addView(btnLiquid, Ui.gap(this));
        root.addView(styleRow, Ui.withTop(this, 6));

        Button btnSave = Ui.pill(this, th, "Сохранить", true);
        btnSave.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { save(); }
        });
        root.addView(btnSave, Ui.withTop(this, 24));

        if (!isNew) {
            Button btnDelete = Ui.pill(this, th, "Удалить профиль", false);
            btnDelete.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { delete(); }
            });
            root.addView(btnDelete, Ui.withTop(this, 10));
        }
    }

    private TextView label(String s) {
        return Ui.text(this, s, 13, th.textDim, false);
    }

    private void refreshStyle() {
        Ui.restyle(this, btnGlass, th, "glass".equals(style));
        Ui.restyle(this, btnLiquid, th, "liquid".equals(style));
    }

    private String joinBreaks(int[] arr) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < arr.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(arr[i]);
        }
        return sb.toString();
    }

    private void save() {
        String name = etName.getText().toString().trim();
        if (name.isEmpty()) name = "Профиль";

        int start = parseTime(etStart.getText().toString().trim());
        int count = parseIntIn(etCount.getText().toString(), 1, 10);
        int lesson = parseIntIn(etLesson.getText().toString(), 10, 180);
        if (start < 0 || count < 0 || lesson < 0) {
            msg("Проверь время начала, количество и длину уроков");
            return;
        }

        int mask = 0;
        for (int i = 0; i < 7; i++) if (dayBoxes[i].isChecked()) mask |= (1 << i);
        if (mask == 0) {
            msg("Выбери хотя бы один учебный день");
            return;
        }

        int need = count - 1;
        int[] breaks = new int[need];
        if (need > 0) {
            String[] parts = etBreaks.getText().toString().split(",");
            if (parts.length != need) {
                msg("Перемен должно быть " + need + ", через запятую");
                return;
            }
            for (int i = 0; i < need; i++) {
                int v = parseIntIn(parts[i], 0, 60);
                if (v < 0) {
                    msg("Перемены: числа от 0 до 60");
                    return;
                }
                breaks[i] = v;
            }
        }

        p.name = name;
        p.startMin = start;
        p.lessonCount = count;
        p.lessonMin = lesson;
        p.breaks = breaks;
        p.days = mask;
        p.widgetStyle = style;

        List<Profile> list = store.getProfiles();
        if (isNew) {
            list.add(p);
            store.setActiveId(p.id);
        } else {
            for (int i = 0; i < list.size(); i++) {
                if (list.get(i).id.equals(p.id)) list.set(i, p);
            }
        }
        store.saveProfiles(list);
        WidgetUpdater.updateAll(this);
        finish();
    }

    private void delete() {
        List<Profile> list = store.getProfiles();
        if (list.size() <= 1) {
            msg("Нельзя удалить единственный профиль");
            return;
        }
        for (int i = 0; i < list.size(); i++) {
            if (list.get(i).id.equals(p.id)) {
                list.remove(i);
                break;
            }
        }
        store.saveProfiles(list);
        store.setActiveId(list.get(0).id);
        WidgetUpdater.updateAll(this);
        finish();
    }

    private int parseTime(String s) {
        String[] t = s.split(":");
        if (t.length != 2) return -1;
        try {
            int h = Integer.parseInt(t[0].trim());
            int m = Integer.parseInt(t[1].trim());
            if (h < 0 || h > 23 || m < 0 || m > 59) return -1;
            return h * 60 + m;
        } catch (NumberFormatException e) {
            return -1;
        }
    }

    private int parseIntIn(String s, int min, int max) {
        try {
            int v = Integer.parseInt(s.trim());
            return (v < min || v > max) ? -1 : v;
        } catch (NumberFormatException e) {
            return -1;
        }
    }

    private void msg(String s) {
        Toast.makeText(this, s, Toast.LENGTH_SHORT).show();
    }
}
