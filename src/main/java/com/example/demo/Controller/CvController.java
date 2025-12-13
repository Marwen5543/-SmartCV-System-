package com.example.demo.Controller;

import com.example.demo.Entity.CvDocument;
import com.example.demo.Service.CvService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/cv")
@CrossOrigin(origins = "http://localhost:4200")
@RequiredArgsConstructor
public class CvController {

    private final CvService cvService;

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadCv(@RequestParam("file") MultipartFile file) {
        Map<String, Object> uploadResult = cvService.uploadCv(file);
        CvDocument savedCv = (CvDocument) uploadResult.get("document");
        Map<String, Object> cvData = (Map<String, Object>) uploadResult.get("cvData");

        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "File uploaded successfully");
        response.put("id", savedCv.getId());
        response.put("fileName", savedCv.getOriginalFileName());
        response.put("cvData", cvData != null ? cvData : getEmptyCvData());

        return ResponseEntity.ok(response);
    }

    private Map<String, Object> getEmptyCvData() {
        // Fallback empty structure if parsing fails
        Map<String, Object> cvData = new HashMap<>();
        cvData.put("personalInfo", new HashMap<>());
        cvData.put("experiences", new java.util.ArrayList<>());
        cvData.put("education", new java.util.ArrayList<>());
        cvData.put("skills", new java.util.ArrayList<>());
        cvData.put("languages", new java.util.ArrayList<>());
        cvData.put("certifications", new java.util.ArrayList<>());
        return cvData;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getCv(@PathVariable Long id) {
        CvDocument cvDocument = cvService.getCv(id);

        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("id", cvDocument.getId());
        response.put("fileName", cvDocument.getOriginalFileName());
        response.put("cvData", cvDocument.getParsedData() != null ?
                cvDocument.getParsedData() : getEmptyCvData());

        return ResponseEntity.ok(response);
    }
}