use axum::{routing::get, Json, Router};
use serde_json::{json, Value};
use std::net::SocketAddr;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let app = Router::new().route("/health", get(health_handler));

    let addr = SocketAddr::from(([0, 0, 0, 0], 8000));
    tracing::info!("Starting Manga OCR Tokio/Axum Server on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;
    Ok(())
}

async fn health_handler() -> Json<Value> {
    Json(json!({
        "status": "ok",
        "service": "manga-ocr-server-rust",
        "version": env!("CARGO_PKG_VERSION")
    }))
}
