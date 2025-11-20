import pytest
from web_server.services.doctor_service import DoctorService
from web_server.settings import Settings


@pytest.fixture
def doctor_service():
    settings = Settings()
    return DoctorService(settings=settings)


def test_get_specialty_for_valid_doctor_id(doctor_service):
    """Test getting specialty for a valid doctor_id."""
    specialty = doctor_service.get_specialty("doctor_heart_1")
    assert specialty == "heart"
    
    specialty = doctor_service.get_specialty("doctor_brain_4")
    assert specialty == "brain"


def test_get_specialty_for_non_existing_doctor_id(doctor_service):
    """Test getting specialty for a non-existing doctor_id raises KeyError."""
    with pytest.raises(KeyError) as exc_info:
        doctor_service.get_specialty("doctor_nonexistent_999")
    
    # Verify the error message is clear and helpful
    assert "doctor_nonexistent_999" in str(exc_info.value)
    assert "not found" in str(exc_info.value).lower()
