export class WorkerPool {
    constructor(workerScript, maxWorkers = 3) {
        this.workerScript = workerScript;
        this.maxWorkers = maxWorkers;
        this.queue = [];
        this.activeWorkers = 0;
    }

    runTask(blob) {
        return new Promise((resolve, reject) => {
            this.queue.push({ blob, resolve, reject });
            this._next();
        });
    }

    _next() {
        if (this.queue.length === 0 || this.activeWorkers >= this.maxWorkers) return;

        const { blob, resolve, reject } = this.queue.shift();
        const worker = new Worker(this.workerScript);
        this.activeWorkers++;

        worker.onmessage = (e) => {
            this.activeWorkers--;
            worker.terminate();

            if (e.data && e.data.error) {
                reject(new Error(e.data.error));
            } else {
                resolve(e.data);
            }

            this._next(); // запускаем следующий
        };

        worker.onerror = (e) => {
            this.activeWorkers--;
            worker.terminate();
            reject(new Error(`Ошибка в воркере: ${e.message}`));
            this._next();
        };

        worker.postMessage(blob);
    }
}