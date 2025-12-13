package com.example.demo.Repository;

import com.example.demo.Entity.CvDocument;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CvRepository extends JpaRepository<CvDocument, Long> {
    // You can add custom queries here later if needed
}
