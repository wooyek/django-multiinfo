=====
Usage
=====

To use MultiInfo for Django in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_multiinfo.apps.DjangoMultiinfoConfig',
        ...
    )

Add MultiInfo for Django's URL patterns:

.. code-block:: python

    from django_multiinfo import urls as django_multiinfo_urls


    urlpatterns = [
        ...
        url(r'^', include(django_multiinfo_urls)),
        ...
    ]
