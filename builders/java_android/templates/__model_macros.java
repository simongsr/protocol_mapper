{% macro build_model(model, models=[]) %}
public class {{ model.name|java.class_name }} extends Model<{{ model.full_name|java.class_name }}> {

    {% for field in model|utils.visit_fields if field.id > 0 %}
        {% if field|utils.is_raw_type %}
    private {{ field|java_android.map_field_type }} m{{ field.name|utils.upper_camel_case }};
        {% elif not field.type|java_android.is_shared_pref_model %}
    private ForeignKeyField<{{ field.type.full_name|java.class_name }}> m{{ field.name|utils.upper_camel_case }}Id;
        {% endif %}
    {% endfor %}



    public {{ model.name|java.class_name }}(Context context) {
        super(context);


        mFieldSet    = Engine.getFieldSet();


        {% for field in model|utils.visit_fields if field.id > 0 %}
            {% if field|utils.is_raw_type %}
        m{{ field.name|utils.upper_camel_case }} = ({{ field|java_android.map_field_type }}) mFieldSet.get(
            {{ model.full_name|java_android.entry_name }}.{{ field|java_android.column_name }});

            {% elif not field.type|java_android.is_shared_pref_model %}
        m{{ field.name|utils.upper_camel_case }}Id = (ForeignKeyField<{{ field.type.full_name|java.class_name }}>) mFieldSet.get(
            {{ model.full_name|java_android.entry_name }}.{{ field|java_android.column_name }});

            {% endif %}
        {% endfor %}
    }


    @Override
    public {{ model.full_name|java.class_name }} loadFromCursor(Cursor cursor, int pos) {
        long _id = cursor.getLong({{ model.full_name|java_android.entry_name }}.INDEX__ID + pos);
        {% for field in model|utils.visit_fields if field.id > 0 %}
            {% if field|utils.is_raw_type %}
                {% if field.type in ['int32', 'uint32', 'sint32', 'fixed32', 'sfixed32', 'int'] %}
        Long {{ field.name|utils.lower_camel_case }} = cursor.get{{ field|java_android.map_cursor_field_type }}({{ model.full_name|java_android.entry_name }}.{{ field|java_android.index_name }} + pos);
                {% elif field.type == 'bool'%}
        {{ field|java.map_reference_field_type }} {{ field.name|utils.lower_camel_case }} = cursor.get{{ field|java_android.map_cursor_field_type }}({{ model.full_name|java_android.entry_name }}.{{ field|java_android.index_name }} + pos) != 0;
                {% else %}
        {{ field|java.map_reference_field_type }} {{ field.name|utils.lower_camel_case }} = cursor.get{{ field|java_android.map_cursor_field_type }}({{ model.full_name|java_android.entry_name }}.{{ field|java_android.index_name }} + pos);
                {% endif %}
            {% elif not field.type|java_android.is_shared_pref_model %}
        long {{ field.name|utils.lower_camel_case }} = cursor.getLong({{ model.full_name|java_android.entry_name }}.{{ field|java_android.index_name }} + pos);
            {% endif %}
        {% endfor %}

        m_ID.setValue(_id);
        {% for field in model|utils.visit_fields if field.id > 0 %}
            {% if field|utils.is_raw_type %}
        m{{ field.name|utils.upper_camel_case }}.setValue({{ field.name|utils.lower_camel_case }});
            {% elif not field.type|java_android.is_shared_pref_model %}
        m{{ field.name|utils.upper_camel_case }}Id.setValue({{ field.name|utils.lower_camel_case }});
            {% endif %}
        {% endfor %}

        return this;
    }

    @Override
    public {{ model.full_name|java.class_name }} saveForeignKeys() throws RequiredConstraintException {
        {% for field in model|utils.visit_fields if field.id > 0 and not field|utils.is_raw_type and not field.type|java_android.is_shared_pref_model %}
        m{{ field.name|utils.upper_camel_case }}Id.save();
        {% endfor %}

        return this;
    }

    @Override
    public {{ model.full_name|java.class_name }} updateForeignKeys() throws RequiredConstraintException {

        {% for field in model|utils.visit_repeated_fields if field.id > 0 %}
            {% if field|utils.is_raw_type %}
        get{{ field.name|utils.upper_camel_case }}(new OnModelsLoadedCallbacks<{{ field.join_model.full_name|java.class_name }}>() {
            @Override
            public void onLoadFinished(ModelSet<{{ field.join_model.full_name|java.class_name }}> modelSet) {

                modelSet.delete(null);

            }
        });

            {% else %}
        get{{ field.name|utils.upper_camel_case }}(new OnModelsLoadedCallbacks<{{ field.type.full_name|java.class_name }}>() {
            @Override
            public void onLoadFinished(ModelSet<{{ field.type.full_name|java.class_name }}> modelSet) {

                for ({{ field.type.full_name|java.class_name }} model : modelSet) {

                    try {

                        remove{{ field.name|utils.upper_camel_case }}(model, null);

                    } catch (PersistentModelNeededException e) {
                        Log.e("{{ model.full_name|java.class_name }}.delete", e.toString());
                    }

                }

            }
        });

            {% endif %}
        {% endfor %}

        return this;
    }

    @Override
    public Uri getUri() {
        if (isSaved())
            return {{ model.full_name|java_android.entry_name }}.buildUriFromId(get_ID());
        return {{ model.full_name|java_android.entry_name }}.CONTENT_URI;
    }

    @Override
    public {{ model.full_name|java.class_name }} save(OnDbActionPerformedCallbacks<{{ model.full_name|java.class_name }}> callbacks) throws RequiredConstraintException {

        {% for field in model|utils.visit_fields if field.id > 0 and field.multiplicity == 'required' %}
            {% if field|utils.is_raw_type %}
        if ( ! m{{ field.name|utils.upper_camel_case }}.isInitialized()) {
            throw new RequiredConstraintException("{{ model.full_name|java.class_name }}: a value for '{{ field.name }}' must be explicitly provided");
        }

            {% elif not field.type|java_android.is_shared_pref_model %}
        if ( ! m{{ field.name|utils.upper_camel_case }}Id.isInitialized()) {
            throw new RequiredConstraintException("{{ model.full_name|java.class_name }}: a value for '{{ field.name }}' must be explicitly provided");
        }

            {% endif %}
        {% endfor %}
        super.save(callbacks);

        return this;
    }

    public {{ model.full_name|java.class_name }} save() throws RequiredConstraintException {
        return save(null);
    }


    public static {{ model.full_name|java.class_name }}.Engine engine(Context context) {
        return new Engine(context);
    }




    {% for field in model|utils.visit_fields if field.id > 0 %}
        {% if field|utils.is_raw_type %}

            {% if field.type in ['date', 'timestamp', 'time'] %}
    public {{ field|java.map_field_type }} get{{ field.name|utils.upper_camel_case }}() {
        long unixTime              = m{{ field.name|utils.upper_camel_case }}.value();

        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTimeInMillis(unixTime);

        return calendar;
    }

    public {{ model.full_name|java.class_name }} set{{ field.name|utils.upper_camel_case }}({{ field|java.map_field_type }} value) {
        long unixTime = value.getTimeInMillis();

        m{{ field.name|utils.upper_camel_case }}.setValue(unixTime);
        setChanged();

        return this;
    }


            {% elif field.type in ['int32', 'uint32', 'sint32', 'fixed32', 'sfixed32', 'int'] %}
    public Long get{{ field.name|utils.upper_camel_case }}() {
        return m{{ field.name|utils.upper_camel_case }}.value();
    }

    public {{ model.full_name|java.class_name }} set{{ field.name|utils.upper_camel_case }}(long value) {
        m{{ field.name|utils.upper_camel_case }}.setValue(value);
        setChanged();

        return this;
    }


            {% else %}
    public {{ field|java.map_field_type }} get{{ field.name|utils.upper_camel_case }}() {
        return m{{ field.name|utils.upper_camel_case }}.value();
    }

    public {{ model.full_name|java.class_name }} set{{ field.name|utils.upper_camel_case }}({{ field|java.map_field_type }} value) {
        m{{ field.name|utils.upper_camel_case }}.setValue(value);
        setChanged();

        return this;
    }


            {% endif %}
        {% elif not field.type|java_android.is_shared_pref_model %}
    public {{ model.full_name|java.class_name }} get{{ field.name|utils.upper_camel_case }}(Model.OnUniqueModelLoadedCallbacks<{{ field.type.full_name|java.class_name }}> callbacks) {
        m{{ field.name|utils.upper_camel_case }}Id.getModel(getContext(), callbacks);

        return this;
    }

    public {{ model.full_name|java.class_name }} set{{ field.name|utils.upper_camel_case }}({{ field.type.full_name|java.class_name }} model) {
        m{{ field.name|utils.upper_camel_case }}Id.setId(model.get_ID());
        setChanged();

        return this;
    }


        {% endif %}
    {% endfor %}





    {% for field in model|utils.visit_repeated_fields %}
            {% if field.id > 0 %}
                {% if field|utils.is_raw_type %}
    public {{ model.full_name|java.class_name }} get{{ field.name|utils.upper_camel_case }}s(final OnRepeatedValuesLoaded<{{ field|java.map_reference_field_type }}> callbacks) {

        if ( ! isSaved()) {

            callbacks.onLoadFinished(new Vector<{{ field|java.map_reference_field_type }}>());

            return this;

        }

        {{ field.join_model.full_name|java.class_name }}.engine(getContext())
            .filter(
                {{ field.join_model.full_name|java.class_name }}.{{ field.join_model.source_field|java_android.column_name }},
                String.valueOf(get_ID())
            )
            .all(new OnModelsLoadedCallbacks<{{ field.join_model.full_name|java.class_name }}>() {
                @Override
                public void onLoadFinished(ModelSet<{{ field.join_model.full_name|java.class_name }}> modelSet) {

                    Vector<{{ field|java.map_reference_field_type }}> values = new Vector<>();

                    for ({{ field.join_model.full_name|java.class_name }} model : modelSet) {

                        {{ field|java.map_reference_field_type }} value = model.get{{ field.join_model.dest_field.name|utils.upper_camel_case }}();

                        values.add(value);

                    }

                    callbacks.onLoadFinished(values);

                }
            });

        return this;
    }

    public {{ model.full_name|java.class_name }} add{{ field.name|utils.upper_camel_case }}(final {{ field|java.map_reference_field_type }} value,
            final OnDbActionPerformedCallbacks<{{ field.join_model.full_name|java.class_name }}> callbacks) throws PersistentModelNeededException {

        if ( ! isSaved())
            throw new PersistentModelNeededException("{{ model.full_name|java.class_name }} model must be saved first");

        new {{ field.join_model.full_name|java.class_name }}(getContext())
            .set{{ field.join_model.dest_field.name|utils.upper_camel_case }}(value)
            .save(callbacks);

        return this;
    }

    public {{ model.full_name|java.class_name }} add{{ field.name|utils.upper_camel_case }}(final {{ field|java.map_reference_field_type }} value) throws PersistentModelNeededException {
        return add{{ field.name|utils.upper_camel_case }}(value, null);
    }

    public {{ model.full_name|java.class_name }} remove{{ field.name|utils.upper_camel_case }}(final {{ field|java.map_reference_field_type }} value,
            final OnDbActionPerformedCallbacks<{{ field.join_model.full_name|java.class_name }}> callbacks) throws PersistentModelNeededException {

        if ( ! isSaved())
            throw new PersistentModelNeededException("{{ model.full_name|java.class_name }} model must be saved first");

        {{ field.join_model.full_name|java.class_name }}.engine(getContext())
            .filter(
                {{ field.join_model.full_name|java_android.entry_name }}.{{ field.join_model.source_field|java_android.column_name }},
                String.valueOf(get_ID())
            )
            .filter(
                {{ field.join_model.full_name|java_android.entry_name }}.{{ field.join_model.dest_field|java_android.column_name }},
                String.valueOf(value)
            )
            .all(new OnModelsLoadedCallbacks<{{ field.join_model.full_name|java.class_name }}>() {
                @Override
                public void onLoadFinished(ModelSet<{{ field.join_model.full_name|java.class_name }}> modelSet) {

                    modelSet.delete(callbacks);

                }
            });

        return this;
    }

    public {{ model.full_name|java.class_name }} remove{{ field.name|utils.upper_camel_case }}(final {{ field|java.map_reference_field_type }} value) throws PersistentModelNeededException {
        return remove{{ field.name|utils.upper_camel_case }}(value, null);
    }

    public {{ model.full_name|java.class_name }} clear{{ field.name|utils.upper_camel_case }}(final OnDbActionPerformedCallbacks<{{ field.join_model.full_name|java.class_name }}> callbacks) throws PersistentModelNeededException {

        if ( ! isSaved())
            throw new PersistentModelNeededException("{{ model.full_name|java.class_name }} model must be saved first");

        {{ field.join_model.full_name|java.class_name }}.engine(getContext())
            .filter(
                {{ field.join_model.full_name|java_android.entry_name }}.{{ field.join_model.source_field|java_android.column_name }},
                String.valueOf(get_ID())
            )
            .all(new OnModelsLoadedCallbacks<{{ field.join_model.full_name|java.class_name }}>() {
                @Override
                public void onLoadFinished(ModelSet<{{ field.join_model.full_name|java.class_name }}> modelSet) {

                    modelSet.delete(callbacks);

                }
            });

        return this;
    }

    public {{ model.full_name|java.class_name }} clear{{ field.name|utils.upper_camel_case }}(final OnDbActionPerformedCallbacks<{{ field.join_model.full_name|java.class_name }}> callbacks) throws PersistentModelNeededException {
        return clear{{ field.name|utils.upper_camel_case }}(null);
    }


                {% elif not field.type|java_android.is_shared_pref_model %}

                    {% if field.join_model.source_field.ref_model == model %}
                        {% set model_column = field.join_model.source_field %}
                        {% set ref_model    = field.join_model.dest_field %}
                    {% else %}
                        {% set model_column = field.join_model.dest_field %}
                        {% set ref_model    = field.join_model.source_field %}
                    {% endif %}


    public {{ model.full_name|java.class_name }} get{{ field.name|utils.upper_camel_case }}s(final OnModelsLoadedCallbacks<{{ field.type.full_name|java.class_name }}> callbacks) {

        if ( ! isSaved()) {

            callbacks.onLoadFinished(new ModelSet<{{ field.type.full_name|java.class_name }}>());

            return this;

        }

        {{ field.join_model.full_name|java.class_name }}.engine(getContext())
            .filter(
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ model_column|java_android.column_name }},
                    String.valueOf(get_ID())
            )
            .all(new OnModelsLoadedCallbacks<{{ field.join_model.full_name|java.class_name }}>() {
                @Override
                public void onLoadFinished(ModelSet<{{ field.join_model.full_name|java.class_name }}> modelSet) {

                    ModelSet<{{ field.type.full_name|java.class_name }}> _modelSet = new ModelSet<>();

                    for ({{ field.join_model.full_name|java.class_name }} model : modelSet) {

                        {{ field.type.full_name|java.class_name }} {{ field.type.name|utils.lower_camel_case }} = model.get{{ field.name|utils.upper_camel_case }}();

                        _modelSet.add({{ field.type.name|utils.lower_camel_case }});

                    }

                    callbacks.onLoadFinished(_modelSet);

                }
            });

        return this;
    }

    public {{ model.full_name|java.class_name }} add{{ field.name|utils.upper_camel_case }}(final {{ ref_model.ref_model.full_name|java.class_name }} model,
            final OnDbActionPerformedCallbacks<{{ field.join_model.full_name|java.class_name }}> callbacks) throws PersistentModelNeededException {

        if ( ! isSaved())
            throw new PersistentModelNeededException("{{ model.full_name|java.class_name }} model must be saved first");

        if ( ! model.isSaved())
            throw new PersistentModelNeededException("{{ ref_model.ref_model.full_name|java.class_name }} model must be saved first");

        final {{ model.full_name|java.class_name }} self = this;

        {{ field.join_model.full_name|java.class_name }}.engine(getContext())
            .filter(
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ model_column|java_android.column_name }},
                    String.valueOf(get_ID())
            )
            .and()
            .filter(
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ ref_model|java_android.column_name }},
                    String.valueOf(model.get_ID())
            )
            .all(new OnModelsLoadedCallbacks<{{ field.join_model.full_name|java.class_name }}>() {
                @Override
                public void onLoadFinished(ModelSet<{{ field.join_model.full_name|java.class_name }}> modelSet) {

                    if (modelSet.size() <= 0)
                        new {{ field.join_model.full_name|java.class_name }}(getContext())
                                .set{{ model.full_name|java.class_name }}(self)
                                .set{{ ref_model.ref_model.full_name|java.class_name }}(model)
                                .save(callbacks);

                }
            });

        return this;
    }

    public {{ model.full_name|java.class_name }} add{{ field.name|utils.upper_camel_case }}({{ ref_model.ref_model.full_name|java.class_name }} model) throws PersistentModelNeededException {
        return add{{ field.name|utils.upper_camel_case }}(model, null);
    }

    public {{ model.full_name|java.class_name }} remove{{ field.name|utils.upper_camel_case }}({{ ref_model.ref_model.full_name|java.class_name }} model,
            final OnDbActionPerformedCallbacks<{{ field.join_model.full_name|java.class_name }}> callbacks) throws PersistentModelNeededException {

        if ( ! isSaved())
            throw new PersistentModelNeededException("{{ model.full_name|java.class_name }} model must be saved first");

        if ( ! model.isSaved())
            throw new PersistentModelNeededException("{{ ref_model.ref_model.full_name|java.class_name }} model must be saved first");

        {{ field.join_model.full_name|java.class_name }}.engine(getContext())
            .filter(
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ model_column|java_android.column_name }},
                    String.valueOf(get_ID())
            )
            .and()
            .filter(
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ ref_model|java_android.column_name }},
                    String.valueOf(model.get_ID())
            )
            .all(new OnModelsLoadedCallbacks<{{ field.join_model.full_name|java.class_name }}>() {
                @Override
                public void onLoadFinished(ModelSet<{{ field.join_model.full_name|java.class_name }}> modelSet) {

                    modelSet.delete(callbacks);

                }
            });

        return this;
    }

    public {{ model.full_name|java.class_name }} remove{{ field.name|utils.upper_camel_case }}({{ ref_model.ref_model.full_name|java.class_name }} model) throws PersistentModelNeededException {
        return remove{{ ref_model.ref_model.full_name|java.class_name }}(model, null);
    }

    public {{ model.full_name|java.class_name }} clear{{ field.name|utils.upper_camel_case }}(final OnDbActionPerformedCallbacks<{{ field.join_model.full_name|java.class_name }}> callbacks) throws PersistentModelNeededException {

        if ( ! isSaved())
            throw new PersistentModelNeededException("{{ model.full_name|java.class_name }} model must be saved first");

        {{ field.join_model.full_name|java.class_name }}.engine(getContext())
            .filter(
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ model_column|java_android.column_name }},
                    String.valueOf(get_ID())
            )
            .all(new OnModelsLoadedCallbacks<{{ field.join_model.full_name|java.class_name }}>() {
                @Override
                public void onLoadFinished(ModelSet<{{ field.join_model.full_name|java.class_name }}> modelSet) {

                    modelSet.delete(callbacks);

                }
            });

        return this;
    }

    public {{ model.full_name|java.class_name }} clear{{ field.name|utils.upper_camel_case }}() throws PersistentModelNeededException {
        return clear{{ field.name|utils.upper_camel_case }}(null);
    }




                {% endif %}
            {% else %}
                {% if field|java_android.is_join_model %}

                    {# if you got here, it means you're trying to generate a
                       custom join model fetch interface;
                       see models.py (__build_graph -> make_reverse_field) #}

                {% else %}
                    {% if 'related_name' in field.modifiers %}
                        {% set field_name = field.modifiers.related_name %}
                    {% else %}
                        {% set field_name = field.name %}
                    {% endif %}
    public {{ model.full_name|java.class_name }} get{{ field_name|utils.upper_camel_case }}(final OnModelsLoadedCallbacks<{{ field.type.full_name|java.class_name }}> callbacks) throws PersistentModelNeededException {

        if ( ! isSaved())
            throw new PersistentModelNeededException("{{ model.full_name|java.class_name }} model must be saved first");

        {{ field.type.full_name|java.class_name }}.engine(getContext())
            .filter(
                {{ field.type.full_name|java_android.entry_name }}.{{ field.field|java_android.column_name }},
                String.valueOf(get_ID())
            )
            .all(callbacks);

        return this;
    }




                {% endif %}
            {% endif %}
        {% endfor %}






    public static class Engine extends Model.Engine<{{ model.full_name|java.class_name }}> {

        {% for field in model|utils.visit_repeated_fields %}
            {% if field.id > 0 %}
                {% if field|utils.is_raw_type %}
        private boolean mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted = false;
                {% elif not field.type|java_android.is_shared_pref_model %}
        private boolean mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted = false;
                {% endif %}
            {% elif not field.type|java_android.is_shared_pref_model %}
                {% if 'related_name' in field.modifiers %}
                    {% set field_name = field.modifiers.related_name %}
                {% else %}
                    {% set field_name = field.name %}
                {% endif %}
        private boolean mIs{{ field_name|utils.upper_camel_case }}ConnectionInserted = false;
            {% endif %}
        {% endfor %}



        public Engine(Context context) {
            super(context);
        }

        @Override
        public {{ model.full_name|java.class_name }} getModelInstance() {
            return new {{ model.full_name|java.class_name }}(getContext());
        }

        @Override
        public Engine newInstance() {
            return new Engine(getContext());
        }

        @Override
        public String[] getColumns() {
            return Model.Engine.qualifyColumns(
                    {{ model.full_name|java_android.entry_name }}.TABLE_NAME,
                    {{ model.full_name|java_android.entry_name }}.COLUMNS
            );
        }

        @Override
        public Uri getUri() {
            return {{ model.full_name|java_android.entry_name }}.CONTENT_URI;
        }

        @Override
        public String getTableName() {
            return {{ model.full_name|java_android.entry_name }}.TABLE_NAME;
        }


        public static FieldSet getFieldSet() {
            try {
                return new FieldSet(new Field[] {

        {% for field in model|utils.visit_fields if field.id > 0 %}
            {% if field|utils.is_raw_type %}
                    // {{ field.name|upper|replace('_', ' ') }}
                    {{ field|java_android.map_field_type }}.builder({{ model.full_name|java_android.entry_name }}.{{ field|java_android.column_name }})
                {% if field|utils.is_unique %}
                        .setUnique(true)
                {% endif %}
                {% if field|utils.is_nullable %}
                        .setNullable(true)
                {% endif %}
                {% if field|utils.has_default_value %}
                        .setDefaultValue({{ field|utils.default_value }})
                {% endif %}
                        .build(),

            {% elif not field.type|java_android.is_shared_pref_model %}
                    // {{ field.name|upper|replace('_', ' ') }} ID
                    ForeignKeyField.builder(
                            {{ model.full_name|java_android.entry_name }}.{{ field|java_android.column_name }},
                            {{ field.type.full_name|java.class_name }}.class
                        )
                        .build(),

            {% endif %}
        {% endfor %}
                });

            } catch (DuplicatedColumnException e) {
                e.printStackTrace();
            }
            return null;
        }


        public static String buildSqlCreateStatement() {
            return Model.Engine.buildSqlCreateStatement(
                    {{ model.full_name|java_android.entry_name }}.TABLE_NAME,
                    getFieldSet()
            );
        }


        public static String buildSqlDropStatement() {
            return Model.Engine.buildSqlDropStatement(
                    {{ model.full_name|java_android.entry_name }}.TABLE_NAME);
        }


        {% for field in model|utils.visit_fields if field.id > 0 and field|utils.version > model|utils.version and field.multiplicity != 'repeated' and (field|utils.is_raw_type or not field.type|java_android.is_shared_pref_model) %}

        public static String buildSqlAdd{{ field.name|utils.upper_camel_case }}FieldStatement() {
            return Model.Engine.buildSqlAddFieldStatement(
                    {{ model.full_name|java_android.entry_name }}.TABLE_NAME,
                    getFieldSet().get({{ model.full_name|java_android.entry_name }}.{{ field|java_android.column_name }})
            );
        }

        {% endfor %}



        {% for field in model|utils.visit_repeated_fields %}
            {% if field.id > 0 %}
                {% if field|utils.is_raw_type %}

// -----------------------------------------------------------------------------

        private void insert{{ field.name|utils.upper_camel_case }}Connection() {

            if (mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted)
                return;

            rawFilter(
                    {{ field.join_model.full_name|java_android.entry_name }}.TABLE_NAME,
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ field.join_model.source_field|java_android.column_name }},
                    {{ field.join_model.source_field.ref_model.full_name|java_android.entry_name }}.TABLE_NAME + "." + {{ field.join_model.source_field.ref_model.full_name|java_android.entry_name }}._ID
            );

            and();

            mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted = true;

        }

        public Engine {{ field.name|utils.lower_camel_case }}Filter({{ field.join_model.dest_field|java.map_field_type }} value) {

            if ( ! mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted)
                insert{{ field.name|utils.upper_camel_case }}Connection();

            String valueStr = String.valueOf(value);

            filter({{ field.join_model.full_name|java_android.entry_name }}.TABLE_NAME,
                   {{ field.join_model.full_name|java_android.entry_name }}.{{ field.join_model.dest_field|java_android.column_name }},
                   valueStr);

            return this;
        }

        public Engine {{ field.name|utils.lower_camel_case }}Exclude({{ field.join_model.dest_field|java.map_field_type }} value) {

            if ( ! mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted)
                insert{{ field.name|utils.upper_camel_case }}Connection();

            String valueStr = String.valueOf(value);

            exclude({{ field.join_model.full_name|java_android.entry_name }}.TABLE_NAME,
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ field.join_model.dest_field|java_android.column_name }},
                    valueStr);

            return this;
        }

// -----------------------------------------------------------------------------

                {% elif not field.type|java_android.is_shared_pref_model %}

// -----------------------------------------------------------------------------


        private void insert{{ field.name|utils.upper_camel_case }}Connection() {

            if (mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted)
                return;

            rawFilter(
                    {{ field.join_model.full_name|java_android.entry_name }}.TABLE_NAME,
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ field.join_model.source_field|java_android.column_name }},
                    {{ field.join_model.source_field.ref_model.full_name|java_android.entry_name }}.TABLE_NAME + "." + {{ field.join_model.source_field.ref_model.full_name|java_android.entry_name }}._ID
            );

            and();

            rawFilter(
                    {{ field.join_model.full_name|java_android.entry_name }}.TABLE_NAME,
                    {{ field.join_model.full_name|java_android.entry_name }}.{{ field.join_model.dest_field|java_android.column_name }},
                    {{ field.join_model.dest_field.ref_model.full_name|java_android.entry_name }}.TABLE_NAME + "." + {{ field.join_model.dest_field.ref_model.full_name|java_android.entry_name }}._ID
            );

            and();

            mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted = true;

        }

        public Engine {{ field.name|utils.lower_camel_case }}Filter(String columnName,
                                    String value) {

            if ( ! mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted)
                insert{{ field.name|utils.upper_camel_case }}Connection();

            filter({{ field.join_model.dest_field.ref_model.full_name|java_android.entry_name }}.TABLE_NAME, columnName, value);

            return this;
        }

        public Engine {{ field.name|utils.lower_camel_case }}Exclude(String columnName,
                                     String value) {

            if ( ! mIs{{ field.name|utils.upper_camel_case }}ConnectionInserted)
                insert{{ field.name|utils.upper_camel_case }}Connection();

            exclude({{ field.join_model.dest_field.ref_model.full_name|java_android.entry_name }}.TABLE_NAME, columnName, value);

            return this;
        }

// -----------------------------------------------------------------------------

                {% endif %}
            {% elif not field.type|java_android.is_shared_pref_model %}
                {% if 'related_name' in field.modifiers %}
                    {% set field_name = field.modifiers.related_name %}
                {% else %}
                    {% set field_name = field.name %}
                {% endif %}

// -----------------------------------------------------------------------------

        private void insert{{ field_name|utils.upper_camel_case }}Connection() {

            if (mIs{{ field_name|utils.upper_camel_case }}ConnectionInserted)
                return;

            rawFilter(
                    {{ field.type.full_name|java_android.entry_name }}.TABLE_NAME,
                    {{ field.type.full_name|java_android.entry_name }}.{{ field.field|java_android.column_name }},
                    {{ model.full_name|java_android.entry_name }}.TABLE_NAME + "." + {{ model.full_name|java_android.entry_name }}._ID
            );

            and();

            mIs{{ field_name|utils.upper_camel_case }}ConnectionInserted = true;

        }

        public Engine {{ field_name|utils.lower_camel_case }}Filter(String columnName,
                                    String value) {

            if ( ! mIs{{ field_name|utils.upper_camel_case }}ConnectionInserted)
                insert{{ field_name|utils.upper_camel_case }}Connection();

            filter({{ field.type.full_name|java_android.entry_name }}.TABLE_NAME, columnName, value);

            return this;
        }

        public Engine {{ field_name|utils.lower_camel_case }}Exclude(String columnName,
                                     String value) {

            if ( ! mIs{{ field_name|utils.upper_camel_case }}ConnectionInserted)
                insert{{ field_name|utils.upper_camel_case }}Connection();

            exclude({{ field.type.full_name|java_android.entry_name }}.TABLE_NAME, columnName, value);

            return this;
        }

// -----------------------------------------------------------------------------

            {% endif %}
        {% endfor %}



    }










    {% for _model in models %}
        {% if _model|java_android.is_shared_pref_model %}
    {{ build_shared_pref_model(_model)|indent }}
        {% else %}
    {{ build_model(_model)|indent }}
        {% endif %}
    {% endfor %}



}

{% endmacro %}





{% macro build_shared_pref_model(model, models=[]) %}

public class {{ model.name|java.class_name }} extends SharedPreferencesModel {

    public {{ model.name|java.class_name }}(Context context) {
        super(
                context,
                {{ model.full_name|java_android.entry_name }}.FILENAME,
                {{ model.full_name|java_android.entry_name }}.MODE
        );
    }


    {% for field in model|utils.visit_fields if field.id > 0 and field|utils.is_raw_type and field.multiplicity != 'repeated' %}

    public {{ field|java.map_field_type }} get{{ field.name|utils.upper_camel_case }}() {
        {{ field|java.map_reference_field_type }} value = get{{ field|java.map_reference_field_type }}({{ model.full_name|java_android.entry_name }}.{{ field.name|java_android.key_name }});
        if (value == null)
            return {{ field|java.default_value }};
        return value;
    }

    public {{ model.full_name|java.class_name }} set{{ field.name|utils.upper_camel_case }}({{ field|java.map_reference_field_type }} value) {
        put({{ model.full_name|java_android.entry_name }}.{{ field.name|java_android.key_name }}, value);

        return this;
    }

    {% endfor %}

}

{% endmacro %}
