package com.springboot_backend.backend_service.controller

import com.springboot_backend.backend_service.model.HealthQuery
import com.springboot_backend.backend_service.model.HealthResponse
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RestController
import com.springboot_backend.backend_service.service.LlmService
import org.springframework.web.bind.annotation.CrossOrigin
import java.util.logging.Logger

@CrossOrigin(origins = ["http://localhost:3000"])
@RestController
class Controller (private val llmService: LlmService) {
    private val logger = Logger.getLogger(Controller::class.java.name)

    @PostMapping("/analyse")
    fun analyzeSymptoms(@RequestBody request: HealthQuery): ResponseEntity<HealthResponse> {
        logger.info("Received symptom analysis request: ${request.symptoms.take(50)}...")

        // Call the LLM service
        val response = llmService.processSymptoms(request)

        return ResponseEntity.ok(response)
    }
}