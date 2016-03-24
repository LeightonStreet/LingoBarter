# coding: utf-8
from lingobarter.core.models.config import Config
from lingobarter.core.models.config import Lingobarter
from lingobarter.utils.populate import Populate


def configure(app, db):
    try:
        is_installed = Lingobarter.objects.get(slug="is_installed")
    except:
        is_installed = False

    if not is_installed:
        app.logger.info("Loading fixtures")
        populate = Populate(
            db,
            filepath=app.config.get('POPULATE_FILEPATH'),
            first_install=True
        )
        try:
            populate.create_configs()
            populate.role("admin")
            populate.role("author")
            try:
                with app.app_context():
                    populate.create_initial_superuser()
            except Exception as e:
                app.logger.warning("Cant create initial user and post: %s" % e)
        except Exception as e:
            import traceback
            traceback.print_exc()
            app.logger.error("Error loading fixtures, try again - %s" % e)
            populate.reset()
            Config.objects.delete()
        else:
            Lingobarter.objects.create(slug="is_installed")
