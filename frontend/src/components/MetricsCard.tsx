import React from 'react';
import styles from '../styles/MetricsCard.module.css';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  trend?: 'up' | 'down' | 'neutral';
}

const MetricsCard: React.FC<MetricsCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  icon,
  trend 
}) => {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        {icon && <span className={styles.icon}>{icon}</span>}
        <h3 className={styles.title}>{title}</h3>
      </div>
      <div className={styles.cardBody}>
        <div className={styles.value}>
          {value}
          {trend && (
            <span className={`${styles.trend} ${styles[trend]}`}>
              {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
            </span>
          )}
        </div>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      </div>
    </div>
  );
};

export default MetricsCard;
