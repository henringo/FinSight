console.log('FinSight Worker starting...');
console.log('Worker environment:', process.env.NODE_ENV || 'development');
console.log('Worker concurrency:', process.env.WORKER_CONCURRENCY || 5);

// Keep the process alive
setInterval(() => {
  console.log(`Worker heartbeat: ${new Date().toISOString()}`);
}, 30000);
