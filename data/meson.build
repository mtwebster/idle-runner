install_data('org.webster.idlerunner.gschema.xml',
    install_dir: join_paths(get_option('datadir'), 'glib-2.0', 'schemas')
)

meson.add_install_script('meson_install_schemas.py')

install_data(
    ['idle-runner.service'],
    install_dir: '/etc/systemd/user'
)

install_data(
    ['idle-runner-cfg.desktop'],
    install_dir: '/usr/share/applications'
)