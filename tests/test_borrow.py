from fastapi import status
import pytest


class TestBorrowBook:
    def test_borrow_book_success(self, client, sample_book_data, sample_member_data):
        """Test successfully borrowing a book when copies are available"""
        # Create a book
        book_response = client.post('/books/', json=sample_book_data)
        book_id = book_response.json()['id']
        
        # Create a member
        member_response = client.post('/members/', json=sample_member_data)
        member_id = member_response.json()['id']
        
        # Borrow the book
        borrow_data = {'book_id': book_id, 'member_id': member_id}
        response = client.post('/borrows/', json=borrow_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'id' in data
        assert data['book_id'] == book_id
        assert data['member_id'] == member_id
        assert 'borrowed_at' in data
        assert 'due_date' in data
        assert data['returned_at'] is None

    def test_borrow_reduces_available_copies(self, client, sample_book_data, sample_member_data):
        """Test that borrowing a book reduces the available_copies count"""
        # Create a book
        book_response = client.post('/books/', json=sample_book_data)
        book_id = book_response.json()['id']
        initial_available = book_response.json()['available_copies']
        
        # Create a member
        member_response = client.post('/members/', json=sample_member_data)
        member_id = member_response.json()['id']
        
        # Borrow the book
        borrow_data = {'book_id': book_id, 'member_id': member_id}
        client.post('/borrows/', json=borrow_data)
        
        # Check that available copies decreased
        book_check = client.get(f'/books/{book_id}')
        assert book_check.status_code == status.HTTP_200_OK
        updated_available = book_check.json()['available_copies']
        assert updated_available == initial_available - 1

    def test_cannot_borrow_when_no_available_copies(self, client, sample_member_data):
        """Test that borrowing fails when no copies are available"""
        # Create a book with only 1 copy
        book_data = {
            'title': 'Limited Edition Book',
            'author': 'Rare Author',
            'isbn': '978-1234567890',
            'total_copies': 1
        }
        book_response = client.post('/books/', json=book_data)
        book_id = book_response.json()['id']
        
        # Create two members
        member1_response = client.post('/members/', json=sample_member_data)
        member1_id = member1_response.json()['id']
        
        member2_data = {
            'full_name': 'Jane Smith',
            'email': 'jane.smith@example.com'
        }
        member2_response = client.post('/members/', json=member2_data)
        member2_id = member2_response.json()['id']
        
        # First member borrows the book successfully
        borrow_data1 = {'book_id': book_id, 'member_id': member1_id}
        response1 = client.post('/borrows/', json=borrow_data1)
        assert response1.status_code == status.HTTP_200_OK
        
        # Second member tries to borrow the same book (should fail)
        borrow_data2 = {'book_id': book_id, 'member_id': member2_id}
        response2 = client.post('/borrows/', json=borrow_data2)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert 'not available' in response2.json()['detail'].lower()

    def test_borrow_book_nonexistent_book(self, client, sample_member_data):
        """Test borrowing a book that doesn't exist"""
        # Create a member
        member_response = client.post('/members/', json=sample_member_data)
        member_id = member_response.json()['id']
        
        # Try to borrow non-existent book
        borrow_data = {'book_id': 99999, 'member_id': member_id}
        response = client.post('/borrows/', json=borrow_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_borrow_book_nonexistent_member(self, client, sample_book_data):
        """Test borrowing with a member that doesn't exist"""
        # Create a book
        book_response = client.post('/books/', json=sample_book_data)
        book_id = book_response.json()['id']
        
        # Try to borrow with non-existent member
        borrow_data = {'book_id': book_id, 'member_id': 99999}
        response = client.post('/borrows/', json=borrow_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'member' in response.json()['detail'].lower()

    def test_member_borrow_limit_of_3_enforced(self, client, sample_member_data):
        """Test that a member cannot borrow more than 3 books at once"""
        # Create a member
        member_response = client.post('/members/', json=sample_member_data)
        member_id = member_response.json()['id']
        
        # Create 4 different books
        books = []
        for i in range(4):
            book_data = {
                'title': f'Book {i+1}',
                'author': f'Author {i+1}',
                'isbn': f'978-000000000{i}',
                'total_copies': 2
            }
            book_response = client.post('/books/', json=book_data)
            books.append(book_response.json()['id'])
        
        # Borrow first 3 books successfully
        for i in range(3):
            borrow_data = {'book_id': books[i], 'member_id': member_id}
            response = client.post('/borrows/', json=borrow_data)
            assert response.status_code == status.HTTP_200_OK
        
        # Try to borrow 4th book - should fail
        borrow_data = {'book_id': books[3], 'member_id': member_id}
        response = client.post('/borrows/', json=borrow_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'borrow limit' in response.json()['detail'].lower()


class TestReturnBook:
    def test_return_book_success(self, client, sample_book_data, sample_member_data):
        """Test successfully returning a borrowed book"""
        # Create book and member
        book_response = client.post('/books/', json=sample_book_data)
        book_id = book_response.json()['id']
        initial_available = book_response.json()['available_copies']
        
        member_response = client.post('/members/', json=sample_member_data)
        member_id = member_response.json()['id']
        
        # Borrow the book
        borrow_data = {'book_id': book_id, 'member_id': member_id}
        borrow_response = client.post('/borrows/', json=borrow_data)
        borrow_id = borrow_response.json()['id']
        
        # Return the book
        return_data = {}
        response = client.post(f'/borrows/{borrow_id}/return', json=return_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['returned_at'] is not None
        
        # Check that available copies increased
        book_check = client.get(f'/books/{book_id}')
        assert book_check.json()['available_copies'] == initial_available

    def test_return_increases_available_copies(self, client, sample_book_data, sample_member_data):
        """Test that returning a book increases the available_copies count"""
        # Create a book
        book_response = client.post('/books/', json=sample_book_data)
        book_id = book_response.json()['id']
        initial_available = book_response.json()['available_copies']
        
        # Create a member
        member_response = client.post('/members/', json=sample_member_data)
        member_id = member_response.json()['id']
        
        # Borrow the book (this reduces available_copies)
        borrow_data = {'book_id': book_id, 'member_id': member_id}
        borrow_response = client.post('/borrows/', json=borrow_data)
        borrow_id = borrow_response.json()['id']
        
        # Check available copies after borrow
        book_after_borrow = client.get(f'/books/{book_id}')
        available_after_borrow = book_after_borrow.json()['available_copies']
        assert available_after_borrow == initial_available - 1
        
        # Return the book
        return_data = {}
        client.post(f'/borrows/{borrow_id}/return', json=return_data)
        
        # Check that available copies increased back to initial
        book_after_return = client.get(f'/books/{book_id}')
        available_after_return = book_after_return.json()['available_copies']
        assert available_after_return == initial_available

    def test_return_book_nonexistent_borrow(self, client):
        """Test returning a borrow record that doesn't exist"""
        return_data = {}
        response = client.post('/borrows/99999/return', json=return_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_return_book_already_returned(self, client, sample_book_data, sample_member_data):
        """Test returning a book that was already returned"""
        # Create book and member
        book_response = client.post('/books/', json=sample_book_data)
        book_id = book_response.json()['id']
        
        member_response = client.post('/members/', json=sample_member_data)
        member_id = member_response.json()['id']
        
        # Borrow and return the book
        borrow_data = {'book_id': book_id, 'member_id': member_id}
        borrow_response = client.post('/borrows/', json=borrow_data)
        borrow_id = borrow_response.json()['id']
        
        return_data = {}
        client.post(f'/borrows/{borrow_id}/return', json=return_data)
        
        # Try to return again
        response = client.post(f'/borrows/{borrow_id}/return', json=return_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'already been returned' in response.json()['detail'].lower()


class TestMemberBorrowHistory:
    def test_get_member_borrow_history(self, client, sample_book_data, sample_member_data):
        """Test retrieving borrow history for a member"""
        # Create book and member
        book_response = client.post('/books/', json=sample_book_data)
        book_id = book_response.json()['id']
        
        member_response = client.post('/members/', json=sample_member_data)
        member_id = member_response.json()['id']
        
        # Borrow the book twice (borrow, return, borrow again)
        borrow_data = {'book_id': book_id, 'member_id': member_id}
        borrow1 = client.post('/borrows/', json=borrow_data)
        borrow1_id = borrow1.json()['id']
        
        # Return first borrow
        client.post(f'/borrows/{borrow1_id}/return', json={})
        
        # Borrow again
        client.post('/borrows/', json=borrow_data)
        
        # Get member history
        response = client.get(f'/borrows/members/{member_id}/borrows')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_get_empty_borrow_history(self, client, sample_member_data):
        """Test getting history for a member with no borrows"""
        member_response = client.post('/members/', json=sample_member_data)
        member_id = member_response.json()['id']
        
        response = client.get(f'/borrows/members/{member_id}/borrows')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
