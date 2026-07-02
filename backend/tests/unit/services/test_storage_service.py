from pathlib import Path
import pytest
from app.services.storage_service import LocalStorageBackend, get_storage_service

@pytest.fixture
def local_storage(tmp_path):
    return LocalStorageBackend(base_dir=str(tmp_path / "uploads"))

@pytest.mark.asyncio
async def test_local_storage_save_and_delete(local_storage, tmp_path):
    class DummyFile:
        def read(self, size=-1):
            if getattr(self, "_read", False):
                return b""
            self._read = True
            return b"dummy content"
            
    # Mocking file obj for shutil.copyfileobj
    import io
    file_obj = io.BytesIO(b"dummy content")
    
    file_url = await local_storage.save_file("resume.pdf", file_obj)
    assert file_url is not None
    assert "resume.pdf" in file_url
    assert Path(file_url).exists()
    
    with open(file_url, "rb") as f:
        assert f.read() == b"dummy content"
        
    await local_storage.delete_file(file_url)
    assert not Path(file_url).exists()

def test_get_storage_service():
    service = get_storage_service()
    assert isinstance(service, LocalStorageBackend)
