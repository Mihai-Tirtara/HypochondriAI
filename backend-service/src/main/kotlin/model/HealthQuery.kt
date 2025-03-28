package model

data class HealthQuery (
    val symptoms: String,
    val userContext: String? = null
)