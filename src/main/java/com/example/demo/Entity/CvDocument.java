package com.example.demo.Entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "cv_documents")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CvDocument {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String fileName;

    @Column(nullable = false)
    private String originalFileName;

    @Column(nullable = false)
    private String status;

    @Column(nullable = false)
    private LocalDateTime uploadDate;

    @Column(columnDefinition = "TEXT")
    private String extractedData;

    // Store parsed CV data as JSON
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "json")
    private Map<String, Object> parsedData;
}