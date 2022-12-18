time = ['year', 'time', 'date', 'day', 'week', 'month']
ordinal = ['ordinal', 'rank', 'leaderboard']

# datatypes to VL datatypes mapping
vl_attribute_types = {
    'Q': 'quantitative',
    'N': 'nominal',
    'T': 'temporal',
    'O': 'ordinal',
}

# we refer to "Calliope: Automatic Visual Data Story Generation
# from a Spreadsheet" about The likelihood of coherence relations,
# including similarity (rs),temporal (rt), contrast (rc),
# cause-effect (ra), elaboration (re), and generalization (rg) used after the 10 fact types.

coherence = {
    "value": {
        "rs": 0.456,
        "rt": 0.089,
        "rc": 0,
        "ra": 0.042,
        "re": 0.268,
        "rg": 0.145,
    },
    "derived_value": {
        "rs": 0.456,
        "rt": 0.089,
        "rc": 0,
        "ra": 0.042,
        "re": 0.268,
        "rg": 0.145,
    },
    "difference": {
        "rs": 0.416,
        "rt": 0.067,
        "rc": 0,
        "ra": 0.058,
        "re": 0.311,
        "rg": 0.148,
    },
    "proportion": {
        "rs": 0.521,
        "rt": 0.073,
        "rc": 0,
        "ra": 0.052,
        "re": 0.224,
        "rg": 0.13,
    },
    "trend": {
        "rs": 0.347,
        "rt": 0.094,
        "rc": 0.082,
        "ra": 0.071,
        "re": 0.282,
        "rg": 0.124,
    },
    "categorization": {
        "rs": 0.377,
        "rt": 0.034,
        "rc": 0,
        "ra": 0.034,
        "re": 0.475,
        "rg": 0.078,
    },
    "distribution": {
        "rs": 0.49,
        "rt": 0.121,
        "rc": 0,
        "ra": 0.044,
        "re": 0.223,
        "rg": 0.121,
    },
    "rank": {
        "rs": 0.438,
        "rt": 0.117,
        "rc": 0,
        "ra": 0.066,
        "re": 0.343,
        "rg": 0.036,
    },
    "correlation": {
        "rs": 0.31,
        "rt": 0.056,
        "rc": 0.151,
        "ra": 0.071,
        "re": 0.262,
        "rg": 0.151,
    },
    "extremum": {
        "rs": 0.518,
        "rt": 0.056,
        "rc": 0,
        "ra": 0.037,
        "re": 0.259,
        "rg": 0.13,
    },
    "outlier": {
        "rs": 0.20,
        "rt": 0.10,
        "rc": 0,
        "ra": 0.10,
        "re": 0.40,
        "rg": 0.20,
    },
}

