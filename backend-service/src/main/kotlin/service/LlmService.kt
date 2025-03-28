package service
import model.HealthQuery
import model.HealthResponse
import org.springframework.beans.factory.annotation.Value
import org.springframework.web.client.RestTemplate
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType

class LlmService {
    @Value("\${llm.service.url}")
    private lateinit var llmServiceUrl: String
    private val restTemplate: RestTemplate = RestTemplate()

    fun processSymptoms(request: HealthQuery): HealthResponse {
        val headers = HttpHeaders().apply {
            contentType = MediaType.APPLICATION_JSON
        }

        val entity = HttpEntity(request, headers)

        return restTemplate.postForObject(
            "$llmServiceUrl/analyse-symptoms",
            entity,
            HealthResponse::class.java
        ) ?: throw RuntimeException("Failed to get response from LLM service")
    }
}
