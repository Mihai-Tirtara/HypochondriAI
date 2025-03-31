package com.springboot_backend.backend_service.model

data class HealthQuery (
    val symptoms: String,
    val userContext: String? = null
)