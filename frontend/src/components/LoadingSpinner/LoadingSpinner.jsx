import styles from './LoadingSpinner.module.css';

const LoadingSpinner = ({ message = 'Running simulation...' }) => {
  return (
    <div className={styles.container}>
      <div className={styles.spinner}></div>
      <p className={styles.message}>{message}</p>
    </div>
  );
};

export default LoadingSpinner;
