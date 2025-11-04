import toast from 'react-hot-toast';

export interface ToastProps {
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive' | 'success';
}

export const useToast = () => {
  const showToast = ({ title, description, variant = 'default' }: ToastProps) => {
    const message = title && description ? `${title}: ${description}` : title || description || '';

    switch (variant) {
      case 'destructive':
        toast.error(message);
        break;
      case 'success':
        toast.success(message);
        break;
      default:
        toast(message);
    }
  };

  return {
    toast: showToast,
  };
};