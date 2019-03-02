install_data('org.webster.idlerunner.gschema.xml',
    install_dir: join_paths(get_option('datadir'), 'glib-2.0', 'schemas')
)

meson.add_install_script('meson_install_schemas.py')

install_data(
    ['idle-runner-autostart.desktop'],
    install_dir: '/etc/xdg/autostart'
)

install_data(
    ['idle-runner-cfg.desktop'],
    install_dir: '/usr/share/applications'
)