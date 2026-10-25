package com.crusty.lessons;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;

public class SettingsActivity extends Activity {

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        final Store store = new Store(this);
        final Theme th = Theme.of(store.getTheme());

        ScrollView sv = new ScrollView(this);
        sv.setBackground(th.background());
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = Ui.dp(this, 20);
        root.setPadding(pad, Ui.dp(this, 48), pad, Ui.dp(this, 28));
        sv.addView(root);

        root.addView(Ui.text(this, "Настройки", 26, th.text, true));
        root.addView(Ui.text(this, "Тема оформления", 13, th.textDim, false),
                Ui.withTop(this, 20));

        String[] keys = {"green", "graphite", "mint"};
        String[] names = {"Тёмно-зелёная", "Графит", "Мята"};
        String current = store.getTheme();
        for (int i = 0; i < keys.length; i++) {
            final String key = keys[i];
            Button b = Ui.pill(this, th, names[i], key.equals(current));
            b.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    store.setTheme(key);
                    recreate();
                }
            });
            root.addView(b, Ui.withTop(this, 8));
        }

        root.addView(Ui.text(this, "Стиль виджета задаётся в редакторе профиля.",
                13, th.textDim, false), Ui.withTop(this, 20));

        root.addView(Ui.text(this, "Создатель @swatlolz", 12, th.textDim, false),
                Ui.withTop(this, 32));
        root.addView(Ui.text(this, "Канал проекта @CrustySearch", 12, th.textDim, false));

        setContentView(sv);
    }
}
