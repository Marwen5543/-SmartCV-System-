package com.example.demo.Service;

import com.example.demo.Exceptions.FileStorageException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.util.UUID;

@Service
public class FileStorageService {

    private final Path fileStorageLocation;

    public FileStorageService(@Value("${file.upload-dir}") String uploadDir) {
        try {
            this.fileStorageLocation = Paths.get(uploadDir).toAbsolutePath().normalize();
            Files.createDirectories(this.fileStorageLocation);
        } catch (Exception ex) {
            throw new RuntimeException("Could not create the directory where the uploaded files will be stored.", ex);
        }
    }

    public String storeFile(MultipartFile file) {
        String originalFileName = file.getOriginalFilename();

        // Check for empty file
        if (file.isEmpty()) {
            throw new FileStorageException("Failed to store empty file.");
        }

        // Check for invalid characters
        if (originalFileName.contains("..")) {
            throw new FileStorageException("Filename contains invalid path sequence " + originalFileName);
        }

        String uniqueFileName = UUID.randomUUID().toString() + "_" + originalFileName;

        try {
            Path targetLocation = this.fileStorageLocation.resolve(uniqueFileName);
            Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);
            return uniqueFileName;
        } catch (IOException ex) {
            // Throw our custom exception here
            throw new FileStorageException("Could not store file " + uniqueFileName + ". Please try again!", ex);
        }
    }
}
