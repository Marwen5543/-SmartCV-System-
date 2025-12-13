package com.example.demo.Exceptions;

public class FileStorageException extends RuntimeException {
    public FileStorageException(String message) {
        super(message);
    }
    public FileStorageException(String message, Throwable cause) {
        super(message, cause);
    }
}
