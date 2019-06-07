"""Tests for Provider Functionality"""
# Protean
from protean.impl.repository.dict_repo import DictProvider
from tests.old.support.dog import Dog, RelatedDog
from tests.old.support.human import Human


class TestProviders:
    """This class holds tests for Providers Singleton"""

    def test_init(self, test_domain):
        """Test that ``providers`` object is available"""
        assert test_domain.providers is not None

    def test_provider_detail(self, test_domain):
        """Test provider info loaded for tests"""

        provider1 = test_domain.providers.get_provider('default')
        assert isinstance(provider1, DictProvider)

    def test_provider_get_connection(self, test_domain):
        """Test ``get_connection`` method and check for connection details"""

        conn = test_domain.providers.get_provider('default').get_connection()
        assert all(key in conn for key in ['data', 'lock', 'counters'])

    def test_provider_raw(self, test_domain):
        """Test raw queries"""
        test_domain.get_repository(Dog).create(name='Murdock', age=7, owner='John')
        test_domain.get_repository(Dog).create(name='Jean', age=3, owner='John')
        test_domain.get_repository(Dog).create(name='Bart', age=6, owner='Carrie')

        # This is a raw query, so should bring results from all repositories
        human = test_domain.get_repository(Human).create(
            first_name='John', last_name='Doe', email='john.doe@gmail.com')
        test_domain.get_repository(RelatedDog).create(name='RelMurdock', age=2, owner=human)

        provider = test_domain.providers.get_provider('default')

        # Filter by Dog attributes
        results = provider.raw('{"owner":"John"}')
        assert isinstance(results, list)
        assert len(results) == 2

        # Try with single quotes in JSON String
        results = provider.raw("{'owner':'John'}")
        assert len(results) == 2

        results = provider.raw('{"owner":"John", "age":3}')
        assert len(results) == 1

        # This query brings results from multiple repositories
        results = provider.raw('{"age__in":[2, 3]}')
        assert len(results) == 2

        results = provider.raw('{"owner":"John", "age__in":[6,7]}')
        assert len(results) == 1

        results = provider.raw('{"owner":"John", "age__in":[2, 3,7]}')
        assert len(results) == 2