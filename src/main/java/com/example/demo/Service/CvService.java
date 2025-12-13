package com.example.demo.Service;

import com.example.demo.Entity.CvDocument;
import com.example.demo.Repository.CvRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class CvService {

    private final FileStorageService fileStorageService;
    private final CvRepository cvRepository;
    private final RestTemplate restTemplate = new RestTemplate();
    private final String PYTHON_API_URL = "http://localhost:8000/extract";

    public Map<String, Object> uploadCv(MultipartFile file) {
        // 1. Save file to disk
        String uniqueFileName = fileStorageService.storeFile(file);

        // 2. Create DB Entry (Initial Status: UPLOADED)
        CvDocument document = CvDocument.builder()
                .fileName(uniqueFileName)
                .originalFileName(file.getOriginalFilename())
                .status("UPLOADED")
                .uploadDate(LocalDateTime.now())
                .build();

        document = cvRepository.save(document);

        // 3. Call Python Worker to extract and parse CV
        Map<String, Object> cvData = null;
        try {
            cvData = extractAndParseCv(document);
        } catch (Exception e) {
            System.err.println("Error calling Python: " + e.getMessage());
            document.setStatus("FAILED");
            cvRepository.save(document);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("document", document);
        result.put("cvData", cvData);
        return result;
    }

    private Map<String, Object> extractAndParseCv(CvDocument document) {
        // Prepare the JSON payload
        Map<String, String> request = new HashMap<>();
        request.put("fileName", document.getFileName());

        // Send POST request to Python
        Map<String, Object> response = restTemplate.postForObject(PYTHON_API_URL, request, Map.class);

        if (response != null) {
            String extractedText = (String) response.get("text");
            Map<String, Object> cvData = (Map<String, Object>) response.get("cvData");

            // Update Database with the result
            document.setExtractedData(extractedText);

            // Store parsed data (you'll need to add this field to CvDocument entity)
            if (cvData != null) {
                document.setParsedData(cvData);
                document.setStatus("COMPLETED");
            } else {
                document.setStatus("PARTIAL");
            }

            cvRepository.save(document);

            return cvData;
        }

        return null;
    }

    public CvDocument getCv(Long id) {
        return cvRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("CV not found with id " + id));
    }
}