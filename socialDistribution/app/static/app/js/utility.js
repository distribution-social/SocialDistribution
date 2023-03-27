//utility funciton
export const extractUUID = (id) => {
    const arr = id.split("/")
    return arr[arr.length - 1]
}

export const uuidToHex = (uuid) => {
    const hex = uuid.replaceAll("-",'');
    return hex;
}
