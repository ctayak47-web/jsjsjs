package com.crusty.lessons;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class Profile {
    public String id;
    public String name;
    public int startMin;        // начало первого урока, минут от полуночи
    public int lessonCount;     // 1..10
    public int lessonMin;       // длина урока в минутах
    public int[] breaks;        // перемены, lessonCount - 1 значений
    public int days;            // маска: бит 0 = Пн ... бит 6 = Вс
    public String widgetStyle;  // "glass" или "liquid"

    public Profile() {
        id = String.valueOf(System.currentTimeMillis());
        name = "Мой профиль";
        startMin = 8 * 60 + 30;
        lessonCount = 6;
        lessonMin = 45;
        breaks = new int[]{5, 5, 10, 5, 5};
        days = 0b0011111;       // Пн–Пт, суббота добавляется в редакторе
        widgetStyle = "glass";
    }

    public JSONObject toJson() throws JSONException {
        JSONObject o = new JSONObject();
        o.put("id", id);
        o.put("name", name);
        o.put("startMin", startMin);
        o.put("lessonCount", lessonCount);
        o.put("lessonMin", lessonMin);
        JSONArray arr = new JSONArray();
        for (int b : breaks) arr.put(b);
        o.put("breaks", arr);
        o.put("days", days);
        o.put("widgetStyle", widgetStyle);
        return o;
    }

    public static Profile fromJson(JSONObject o) throws JSONException {
        Profile p = new Profile();
        p.id = o.getString("id");
        p.name = o.getString("name");
        p.startMin = o.getInt("startMin");
        p.lessonCount = o.getInt("lessonCount");
        p.lessonMin = o.getInt("lessonMin");
        JSONArray arr = o.getJSONArray("breaks");
        p.breaks = new int[arr.length()];
        for (int i = 0; i < arr.length(); i++) p.breaks[i] = arr.getInt(i);
        p.days = o.getInt("days");
        p.widgetStyle = o.getString("widgetStyle");
        return p;
    }
}
