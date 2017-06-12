package {{ package }};

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

{% for model in schema|core.models(reverse=True) %}
import {{ package }}.models.{{ model|java.class_name }};
{% endfor %}

/**
 * Created by ProtocolMapper on {{ now }}.
 */
public class {{ helper_name }} extends SQLiteOpenHelper {

    private static final int DATABASE_VERSION = {{ schema|core.version }};

    public  static final String DATABASE_NAME = "{{ package }}{{ appname|lower }}.db";




    public {{ helper_name }}(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }




    @Override
    public void onCreate(SQLiteDatabase db) {

        {% for model in schema|core.models(reverse=True) if not model|java_android.is_shared_pref_model %}
        final String SQL_CREATE_TABLE__{{ model.fullname|join('__')|upper }} = {{ model|java.class_name }}.Engine.buildSqlCreateStatement();
        {% endfor %}

        {% for model in schema|core.models(reverse=True) if not model|java_android.is_shared_pref_model %}
        db.execSQL(SQL_CREATE_TABLE__{{ model.fullname|join('__')|upper }});
        {% endfor %}
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
    {% set higher_version = schema|core.version %}
    {% if higher_version > 1 %}

        if (newVersion > oldVersion) {

            {% for version in range(2, higher_version + 1) %}
            // version {{ version }}
            if (oldVersion < {{ version }} && newVersion >= {{ version }}) {

                {% for model in schema|core.models(reverse=True) if not model|java_android.is_shared_pref_model %}
                    {% if model|core.version == version %}
                    final String SQL_CREATE_TABLE__{{ model.fullname|join('__')|upper }} = {{ model|java.class_name }}.Engine.buildSqlCreateStatement();

                    db.execSQL(SQL_CREATE_TABLE__{{ model.fullname|join('__')|upper }});
                    {% endif %}
                    {% for field in model|java_android.fields if field|core.version == version %}
                    final String SQL_ALTER_TABLE__{{ model.fullname|join('__')|upper }}___{{ field.name|upper }} = {{ model|java.class_name }}.Engine.buildSqlAdd{{ field.name|core.upper_camel_case }}FieldStatement();

                    db.execSQL(SQL_ALTER_TABLE__{{ model.fullname|join('__')|upper }}___{{ field.name|upper }});
                    {% endfor %}

                {% endfor %}
            }

            {% endfor %}
        }
    {% endif %}
    }

}

