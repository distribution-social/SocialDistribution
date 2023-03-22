//utility funciton
export const extractUUID = (id) => {
    const arr = id.split("/")
    return arr[arr.length - 1]
}
