package {{ package }}.models;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.util.Log;

import java.util.Calendar;
import java.util.GregorianCalendar;

{% set lib_package = "com.orangelabs.grapefruit" %}
{% if model|java_android.contains_models %}
import {{ lib_package }}.Model;
{% endif%}
{% if model|java_android.contains_shared_pref_models %}
import {{ lib_package }}.SharedPreferencesModel;
{% endif%}
{% for field_type in model|java_android.gen_imported_fields %}
import {{ lib_package }}.{{ field_type }};
{% endfor %}
import {{ lib_package }}.FieldSet;
import {{ lib_package }}.Field;
import {{ lib_package }}.DuplicatedColumnException;
import {{ lib_package }}.PersistentModelNeededException;
import {{ lib_package }}.RequiredConstraintException;

{% for entry_name in model|java_android.gen_imported_entries %}
import {{ package }}.{{ contract_name }}.{{ entry_name }};
{% endfor %}

{% for model_name in model|java_android.gen_imported_models %}
import {{ package }}.models.{{ model_name }};
{% endfor %}

/**
 * Created by ProtocolMapper on {{ now }}.
 */
{% import '__model_macros.java.jinja' as macros %}
{% if model|java_android.is_shared_pref_model %}
{{ macros.build_shared_pref_model(model, models) }}
{% else %}
{{ macros.build_model(model, models) }}
{% endif %}

