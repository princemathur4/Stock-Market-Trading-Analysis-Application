require.config({
    shim: {
        'bootstrap': ['jquery'],
        'sparkline': ['jquery'],
        'tablesorter': ['jquery'],
        'vector-map': ['jquery'],
        'vector-map-de': ['vector-map', 'jquery'],
        'vector-map-world': ['vector-map', 'jquery'],
        'core': ['bootstrap', 'jquery'],
    },
    paths: {
        'core': '/static/assets/js/core',
        'jquery': '/static/assets/js/vendors/jquery.min',
        'bootstrap': '/static/assets/js/vendors/bootstrap.bundle.min',
        'sparkline': '/static/assets/js/vendors/jquery.sparkline.min',
        'selectize': '/static/assets/js/vendors/selectize.min',
        'tablesorter': '/static/assets/js/vendors/jquery.tablesorter.min',
        'vector-map': '/static/assets/js/vendors/jquery-jvectormap-2.0.3.min',
        'vector-map-de': '/static/assets/js/vendors/jquery-jvectormap-de-merc',
        'vector-map-world': '/static/assets/js/vendors/jquery-jvectormap-world-mill',
        'circle-progress': '/static/assets/js/vendors/circle-progress.min',
    }
});

require(['core']);
