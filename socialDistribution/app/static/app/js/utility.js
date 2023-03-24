//utility funciton
export const extractUUID = (id) => {
    console.log(id)
    const arr = id.split("/")
    return arr[arr.length - 1]
}
