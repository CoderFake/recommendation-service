"use client"

import { useState, useEffect, useCallback } from "react"

import type { ToastActionElement, ToastProps } from "@/components/ui/toast"

const TOAST_LIMIT = 5
const TOAST_REMOVE_DELAY = 5000

type ToasterToast = ToastProps & {
    id: string
    title?: React.ReactNode
    description?: React.ReactNode
    action?: ToastActionElement
}

const actionTypes = {
    ADD_TOAST: "ADD_TOAST",
    UPDATE_TOAST: "UPDATE_TOAST",
    DISMISS_TOAST: "DISMISS_TOAST",
    REMOVE_TOAST: "REMOVE_TOAST",
} as const

let count = 0

function genId() {
    count = (count + 1) % Number.MAX_SAFE_INTEGER
    return count.toString()
}

type ActionType = typeof actionTypes

type Action =
    | {
        type: ActionType["ADD_TOAST"]
        toast: ToasterToast
    }
    | {
        type: ActionType["UPDATE_TOAST"]
        toast: Partial<ToasterToast>
        id: string
    }
    | {
        type: ActionType["DISMISS_TOAST"]
        id: string
    }
    | {
        type: ActionType["REMOVE_TOAST"]
        id: string
    }
interface State {
    toasts: ToasterToast[]
}

const toastTimeouts = new Map<string, ReturnType<typeof setTimeout>>()

const reducer = (state: State, action: Action): State => {
    switch (action.type) {
        case actionTypes.ADD_TOAST:
            return {
                ...state,
                toasts: [action.toast, ...state.toasts].slice(0, TOAST_LIMIT),
            }

        case actionTypes.UPDATE_TOAST:
            return {
                ...state,
                toasts: state.toasts.map((t) =>
                    t.id === action.id ? { ...t, ...action.toast } : t
                ),
            }

        case actionTypes.DISMISS_TOAST: {
            const { id } = action

            if (state.toasts.find((t) => t.id === id) === undefined) {
                return state
            }

            return {
                ...state,
                toasts: state.toasts.map((t) =>
                    t.id === id
                        ? {
                            ...t,
                            open: false,
                        }
                        : t
                ),
            }
        }

        case actionTypes.REMOVE_TOAST:
            if (action.id === undefined) {
                return {
                    ...state,
                    toasts: [],
                }
            }
            return {
                ...state,
                toasts: state.toasts.filter((t) => t.id !== action.id),
            }
    }
}

const listeners: ((state: State) => void)[] = []

let memoryState: State = { toasts: [] }

function dispatch(action: Action) {
    memoryState = reducer(memoryState, action)
    listeners.forEach((listener) => {
        listener(memoryState)
    })
}

type Toast = Omit<ToasterToast, "id">

function toast({ ...props }: Toast) {
    const id = genId()

    const update = (props: ToasterToast) =>
        dispatch({
            type: actionTypes.UPDATE_TOAST,
            id,
            toast: props,
        })

    const dismiss = () => dispatch({ type: actionTypes.DISMISS_TOAST, id })

    dispatch({
        type: actionTypes.ADD_TOAST,
        toast: {
            ...props,
            id,
            open: true,
            onOpenChange: (open) => {
                if (!open) dismiss()
            },
        },
    })

    if (toastTimeouts.has(id)) {
        clearTimeout(toastTimeouts.get(id))
    }

    toastTimeouts.set(
        id,
        setTimeout(() => {
            dispatch({ type: actionTypes.DISMISS_TOAST, id })

            setTimeout(() => {
                dispatch({ type: actionTypes.REMOVE_TOAST, id })
                toastTimeouts.delete(id)
            }, 300) // thời gian chuyển đổi animation
        }, TOAST_REMOVE_DELAY)
    )

    return {
        id,
        dismiss,
        update,
    }
}

function useToast() {
    const [state, setState] = useState<State>(memoryState)

    useEffect(() => {
        listeners.push(setState)
        return () => {
            const index = listeners.indexOf(setState)
            if (index > -1) {
                listeners.splice(index, 1)
            }
        }
    }, [state])

    return {
        ...state,
        toast,
        dismiss: (id?: string) => {
            if (id) {
                dispatch({ type: actionTypes.DISMISS_TOAST, id })
            }
        },
    }
}

export { useToast, toast }