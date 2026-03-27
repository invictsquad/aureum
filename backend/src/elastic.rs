/// Aureum Elastic Controller — Native Resilience
///
/// Elasticity system that automatically adapts processing scale
/// based on load and latency, ensuring the system never crashes.
///
/// Concept: "AI that Breathes"
/// - Inhale (low load): expands accuracy
/// - Exhale (high load): contracts accuracy
/// - Continuous breathing: automatic adaptation
///
/// Author: Luiz Antônio De Lima Mendonça
/// Location: Resende, RJ, Brazil
/// Instagram: @luizinvict
/// Date: 2026-03-26

use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};

/// Elasticity controller for Aureum models
///
/// Monitors latency and automatically adjusts scale to keep
/// the system responsive even under extreme load.
#[repr(C)]
pub struct ElasticController {
    /// Current scale (0.0 to 1.0) stored as f32 bits
    current_scale: AtomicU64,
    
    /// Request counter since last adjustment
    request_count: AtomicUsize,
    
    /// Sum of latencies (ms) since last adjustment
    total_latency_ms: AtomicU64,
    
    /// Minimum allowed scale (e.g., 0.1 = 10% accuracy)
    min_scale: f32,
    
    /// Maximum allowed scale (e.g., 1.0 = 100% accuracy)
    max_scale: f32,
    
    /// Target latency in milliseconds
    target_latency_ms: u64,
    
    /// Adjustment interval (number of requests)
    adjustment_interval: usize,
}

impl ElasticController {
    /// Creates new elastic controller
    ///
    /// # Parameters
    /// - `min_scale`: Minimum scale (0.0 to 1.0)
    /// - `max_scale`: Maximum scale (0.0 to 1.0)
    /// - `target_latency_ms`: Target latency in milliseconds
    ///
    /// # Example
    /// ```no_run
    /// use aureum_kernel::elastic::ElasticController;
    /// let controller = ElasticController::new(0.1, 1.0, 100);
    /// // System will maintain latency at ~100ms
    /// // Degrading from 100% down to 10% accuracy if needed
    /// ```
    pub fn new(min_scale: f32, max_scale: f32, target_latency_ms: u64) -> Self {
        assert!(min_scale > 0.0 && min_scale <= 1.0);
        assert!(max_scale > 0.0 && max_scale <= 1.0);
        assert!(min_scale <= max_scale);
        
        Self {
            current_scale: AtomicU64::new(max_scale.to_bits() as u64),
            request_count: AtomicUsize::new(0),
            total_latency_ms: AtomicU64::new(0),
            min_scale,
            max_scale,
            target_latency_ms,
            adjustment_interval: 100,
        }
    }
    
    /// Gets current scale
    ///
    /// # Returns
    /// Value between min_scale and max_scale
    pub fn get_scale(&self) -> f32 {
        let bits = self.current_scale.load(Ordering::Relaxed);
        f32::from_bits(bits as u32)
    }
    
    /// Records latency of a request
    ///
    /// Accumulates latencies and adjusts scale periodically
    ///
    /// # Parameters
    /// - `latency_ms`: Request latency in milliseconds
    pub fn record_request(&self, latency_ms: u64) {
        let count = self.request_count.fetch_add(1, Ordering::Relaxed) + 1;
        self.total_latency_ms.fetch_add(latency_ms, Ordering::Relaxed);
        
        // Adjust scale every N requests
        if count % self.adjustment_interval == 0 {
            self.adjust_scale();
        }
    }
    
    /// Adjusts scale based on average latency
    ///
    /// Algorithm:
    /// - If latency > target: reduce scale (less accuracy, more speed)
    /// - If latency < target: increase scale (more accuracy, same speed)
    fn adjust_scale(&self) {
        let count = self.request_count.load(Ordering::Relaxed);
        let total_latency = self.total_latency_ms.load(Ordering::Relaxed);
        
        if count == 0 {
            return;
        }
        
        let avg_latency = total_latency / count as u64;
        let current_scale = self.get_scale();
        
        let new_scale = if avg_latency > self.target_latency_ms {
            // High latency: EXHALE (reduce scale)
            let ratio = avg_latency as f32 / self.target_latency_ms as f32;
            let reduction = current_scale / ratio;
            reduction.max(self.min_scale)
        } else {
            // Low latency: INHALE (increase scale)
            let ratio = self.target_latency_ms as f32 / avg_latency as f32;
            let increase = current_scale * ratio.min(1.2); // Maximum 20% increase per cycle
            increase.min(self.max_scale)
        };
        
        // Update scale atomically
        self.current_scale.store(new_scale.to_bits() as u64, Ordering::Relaxed);
        
        // Reset counters for next cycle
        self.request_count.store(0, Ordering::Relaxed);
        self.total_latency_ms.store(0, Ordering::Relaxed);
    }
    
    /// Gets controller statistics
    pub fn stats(&self) -> ElasticStats {
        let count = self.request_count.load(Ordering::Relaxed);
        let total_latency = self.total_latency_ms.load(Ordering::Relaxed);
        let avg_latency = if count > 0 {
            total_latency / count as u64
        } else {
            0
        };
        
        ElasticStats {
            current_scale: self.get_scale(),
            avg_latency_ms: avg_latency,
            request_count: count,
            min_scale: self.min_scale,
            max_scale: self.max_scale,
            target_latency_ms: self.target_latency_ms,
        }
    }
}

/// Elastic controller statistics
#[repr(C)]
#[derive(Debug, Clone)]
pub struct ElasticStats {
    pub current_scale: f32,
    pub avg_latency_ms: u64,
    pub request_count: usize,
    pub min_scale: f32,
    pub max_scale: f32,
    pub target_latency_ms: u64,
}

// ─── FFI for Python ───────────────────────────────────────────────────────────

/// Creates new elastic controller (FFI)
#[no_mangle]
pub extern "C" fn aureum_elastic_new(
    min_scale: f32,
    max_scale: f32,
    target_latency_ms: u64
) -> *mut ElasticController {
    Box::into_raw(Box::new(ElasticController::new(
        min_scale,
        max_scale,
        target_latency_ms
    )))
}

/// Gets current scale (FFI)
#[no_mangle]
pub extern "C" fn aureum_elastic_get_scale(controller: *const ElasticController) -> f32 {
    if controller.is_null() {
        return 1.0;
    }
    unsafe { (*controller).get_scale() }
}

/// Records request latency (FFI)
#[no_mangle]
pub extern "C" fn aureum_elastic_record(controller: *mut ElasticController, latency_ms: u64) {
    if controller.is_null() {
        return;
    }
    unsafe { (*controller).record_request(latency_ms) }
}

/// Gets statistics (FFI)
#[no_mangle]
pub extern "C" fn aureum_elastic_stats(
    controller: *const ElasticController,
    stats: *mut ElasticStats
) {
    if controller.is_null() || stats.is_null() {
        return;
    }
    unsafe {
        *stats = (*controller).stats();
    }
}

/// Frees controller memory (FFI)
#[no_mangle]
pub extern "C" fn aureum_elastic_free(controller: *mut ElasticController) {
    if !controller.is_null() {
        unsafe {
            drop(Box::from_raw(controller));
        }
    }
}

// ─── Tests ────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_elastic_creation() {
        let controller = ElasticController::new(0.1, 1.0, 100);
        assert_eq!(controller.get_scale(), 1.0); // Starts at maximum
    }
    
    #[test]
    fn test_elastic_scale_down() {
        let controller = ElasticController::new(0.1, 1.0, 100);
        
        // Simulate 100 requests with high latency (200ms)
        for _ in 0..100 {
            controller.record_request(200);
        }
        
        // Scale should have reduced
        let scale = controller.get_scale();
        assert!(scale < 1.0);
        assert!(scale >= 0.1);
    }
    
    #[test]
    fn test_elastic_scale_up() {
        let controller = ElasticController::new(0.1, 1.0, 100);
        
        // Force low scale
        controller.current_scale.store(0.5f32.to_bits() as u64, Ordering::Relaxed);
        
        // Simulate 100 requests with low latency (50ms)
        for _ in 0..100 {
            controller.record_request(50);
        }
        
        // Scale should have increased
        let scale = controller.get_scale();
        assert!(scale > 0.5);
        assert!(scale <= 1.0);
    }
    
    #[test]
    fn test_elastic_bounds() {
        let controller = ElasticController::new(0.2, 0.8, 100);
        
        // Extremely high latency
        for _ in 0..100 {
            controller.record_request(1000);
        }
        
        // Should not go below minimum
        assert!(controller.get_scale() >= 0.2);
        
        // Extremely low latency
        for _ in 0..100 {
            controller.record_request(10);
        }
        
        // Should not go above maximum
        assert!(controller.get_scale() <= 0.8);
    }
    
    #[test]
    fn test_elastic_stats() {
        let controller = ElasticController::new(0.1, 1.0, 100);
        
        for _ in 0..50 {
            controller.record_request(150);
        }
        
        let stats = controller.stats();
        assert_eq!(stats.request_count, 50);
        assert_eq!(stats.avg_latency_ms, 150);
        assert_eq!(stats.target_latency_ms, 100);
    }
}
