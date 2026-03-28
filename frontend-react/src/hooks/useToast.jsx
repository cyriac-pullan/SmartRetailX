import { useAppStore } from '../store/useAppStore'

export const useToast = () => {
    const pushToast = useAppStore((state) => state.pushToast)
    const dismissToast = useAppStore((state) => state.dismissToast)

    const toast = (message, type = 'info', duration = 4000) => {
        pushToast({ message, type, duration })
    }

    return {
        toast,
        dismiss: dismissToast
    }
}
