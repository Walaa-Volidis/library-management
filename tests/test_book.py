from fastapi import status

class TestCreateBook:
    def test_create_book_success(self, client, sample_book_data):
        response = client.post('/books/', json=sample_book_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'id' in data
        assert data['title'] == sample_book_data['title']
        assert data['author'] == sample_book_data['author']
        assert data['available_copies'] == sample_book_data['total_copies']

    def test_create_book_missing_field(self, client):
        incomplete_data = {'title': 'Test', 'author': 'Author'}
        response = client.post('/books/', json=incomplete_data)
        assert response.status_code == 422  # Unprocessable Entity

class TestListBooks:
    def test_list_empty_database(self, client):
        response = client.get('/books/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_multiple_books(self, client, sample_book_data):
        client.post('/books/', json=sample_book_data)
        second_book = {'title': 'Design Patterns', 'author': 'Gang of Four', 'isbn': '978-0201633612', 'total_copies': 3}
        client.post('/books/', json=second_book)
        response = client.get('/books/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
