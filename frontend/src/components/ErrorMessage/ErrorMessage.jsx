import styles from './ErrorMessage.module.css';

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className={styles.container}>
      <div className={styles.icon}>⚠️</div>
      <h3 className={styles.title}>Error</h3>
      <p className={styles.message}>{message}</p>
      {onRetry && (
        <button className={styles.retryButton} onClick={onRetry}>
          Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
