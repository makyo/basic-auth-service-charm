#!/usr/bin/env python3

from os import path
import sys
import traceback

sys.path.extend([
    'lib',
    '.',
    path.join(
        path.dirname(__file__),
        '..',
        '..',
        '.venv',
        'lib',
        'python3.5',
        'site-packages')])

from charmhelpers.core import hookenv, host

from reactive.basic_auth import (
    install,
    perform_database_migrations,
)

SERVICE_JOB = "snap.basic-auth-service.basic-auth-service"


def pause():
    """Stop basic-auth-service service."""
    hookenv.status_set("maintenance", "Stopping service: basic-auth-service.")
    host.service_pause(SERVICE_JOB)
    hookenv.status_set(
        "blocked", "Service paused: use 'resume' action to restart.")


def resume():
    """Restart basic-auth-service service."""
    hookenv.status_set(
        "maintenance", "Restarting service: basic-auth-service.")
    host.service_resume(SERVICE_JOB)
    hookenv.status_set("active", "Service up and running.")


def upgrade():
    """Upgrade basic-auths-service snap."""
    install()
    # XXX Work-around a bug in the snap that restarts the service even
    # when disabled: disable it again.
    host.service_pause(SERVICE_JOB)
    hookenv.status_set("maintenance", "Service upgraded and paused.")


def schema_upgrade():
    """Perform database migrations for the service."""
    perform_database_migrations(None)
    # XXX Work-around a bug in the snap that restarts the service even
    # when disabled: disable it again.
    host.service_pause(SERVICE_JOB)


ACTIONS = {
    "pause": pause,
    "resume": resume,
    "schema-upgrade": schema_upgrade,
    "upgrade": upgrade,
}


def main():
    action_name = hookenv.action_name()
    try:
        action = ACTIONS[action_name]
    except KeyError:
        return "Action '{}' undefined".format(action_name)

    try:
        action()
    except Exception as e:
        details = {"traceback": traceback.format_exc()}
        hookenv.action_set(details)
        hookenv.action_fail(str(e))


if __name__ == "__main__":
    sys.exit(main())
