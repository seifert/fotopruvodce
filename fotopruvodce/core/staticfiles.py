from django.contrib.staticfiles import storage


class ManifestStaticFilesStorage(storage.ManifestStaticFilesStorage):

    max_post_process_passes = 50
    manifest_strict = False
