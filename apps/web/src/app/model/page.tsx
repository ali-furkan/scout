interface Model {
    base_models: string[];
}

export default async function ModelPage() {
    const data = await fetch("http://127.0.0.1:5001/model").then((res) => res.json());
    return (
        <div className="mx-auto p-4 max-w-6xl">
            <h1 className="text-4xl font-bold text-center">Model</h1>
            <div className="mt-5">
                <h3 className="text-xl font-bold">Summary</h3>
                <ul className="list-disc list-inside ml-3 my-2">
                    <li>Model Name: <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded-md text-sm my-2" >{data.model.name} </code> </li>
                    <li>Type: <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded-md text-sm my-2" >{data.model.type} </code> </li>
                </ul>
                <p>
                    This model is a combination of the following base models:{"\n"}
                </p>
                <ul className="list-disc list-inside ml-3 my-2">
                    {data.model.base_models.map((model: string) => (
                        <li>{model}</li>
                    ))}
                </ul>
                <p>
                    And These are the features used in the model:
                    <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md text-sm my-2">
                        {JSON.stringify(data.model.features_names, null, 2)}
                    </pre>
                </p>
                <h3 className="text-xl font-bold">Verbose</h3>
                <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md text-sm">
                    {JSON.stringify(data, null, 2)}
                </pre>
            </div>
        </div>
    )
}