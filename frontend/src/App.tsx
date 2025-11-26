import {useState} from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from "remark-gfm";
import {Upload, RefreshCw, Loader2, FileImage, AlertCircle} from 'lucide-react';
import * as React from "react";

export default function App() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [prediction, setPrediction] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target?.files?.[0];
        if (file) {
            setError(null);
            setPrediction("");
            setSelectedFile(file);
            // Create a temporary URL to display the image immediately
            setPreviewUrl(URL.createObjectURL(file));
        }
    };

    const handleSubmit = async () => {
        if (!selectedFile) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('image', selectedFile);

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }

            const data = await response.json();

            setPrediction(data.article || data.text || "No content returned.");

        } catch (err) {
            setError((err as {message:string}).message || "Failed to analyze image.");
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setSelectedFile(null);
        setPreviewUrl(null);
        setPrediction("");
        setError(null);
    };

    return (
        <div className="min-h-screen bg-gray-50 text-gray-800 font-sans p-6 md:p-12">
            <div className="max-w-6xl mx-auto">

                <header className="mb-10 text-center">
                    <h1 className="text-4xl font-extrabold text-indigo-900 tracking-tight mb-2">
                        Plant care instructions
                    </h1>
                    <p className="text-gray-500">
                        Upload an image of a plant to find more information about it.
                    </p>
                </header>

                <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 min-h-[600px]">

                    {!previewUrl ? (
                        <div
                            className="h-full min-h-[500px] flex flex-col items-center justify-center p-10 bg-gray-50/50 border-2 border-dashed border-gray-300 m-4 rounded-xl hover:bg-indigo-50/30 transition-colors">
                            <div className="bg-white p-4 rounded-full shadow-sm mb-4">
                                <Upload className="w-8 h-8 text-indigo-600"/>
                            </div>
                            <h3 className="text-xl font-semibold text-gray-700 mb-2">Upload your image</h3>
                            <p className="text-gray-400 mb-6 text-center max-w-xs">
                                JPG only. The AI will analyze the image and come with insights into how to take care of
                                the plant.
                            </p>
                            <label
                                className="cursor-pointer bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-all shadow-md hover:shadow-lg transform active:scale-95">
                                <span>Select Image</span>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileChange}
                                    className="hidden"
                                />
                            </label>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-2 h-full min-h-[600px]">

                            <div
                                className="bg-gray-100 p-8 flex flex-col items-center justify-start border-b lg:border-b-0 lg:border-r border-gray-200 relative">
                                <div className="sticky top-8 w-full flex flex-col items-center">
                                    <div
                                        className="relative w-full aspect-video bg-gray-200 rounded-lg shadow-md overflow-hidden mb-6">
                                        <img
                                            src={previewUrl}
                                            alt="Preview"
                                            className="w-full h-full object-contain bg-black/5"
                                        />
                                    </div>

                                    <div className="flex gap-4 w-full">
                                        {!prediction && !loading && (
                                            <button
                                                onClick={handleSubmit}
                                                className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-3 px-4 rounded-lg font-semibold shadow-sm transition-all flex items-center justify-center gap-2"
                                            >
                                                <RefreshCw className="w-4 h-4"/>
                                                Generate Article
                                            </button>
                                        )}

                                        <button
                                            onClick={resetForm}
                                            className={`py-3 px-4 rounded-lg font-medium border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 transition-all ${!prediction && !loading ? 'w-auto' : 'w-full'}`}
                                        >
                                            Upload Different Image
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="p-8 lg:p-10 bg-white overflow-y-auto max-h-[900px]">

                                {loading && (
                                    <div
                                        className="h-full flex flex-col items-center justify-center text-center min-h-[300px]">
                                        <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4"/>
                                        <h3 className="text-lg font-semibold text-gray-800">Analyzing image...</h3>
                                        <p className="text-gray-400 mt-2">Running CNN Model • Searching Tavily •
                                            Generating Text</p>
                                    </div>
                                )}

                                {!loading && error && (
                                    <div
                                        className="h-full flex flex-col items-center justify-center text-center min-h-[300px] text-red-500">
                                        <AlertCircle className="w-12 h-12 mb-4"/>
                                        <h3 className="text-lg font-bold">Something went wrong</h3>
                                        <p className="mt-2 text-red-400 bg-red-50 px-4 py-2 rounded">{error}</p>
                                    </div>
                                )}

                                {!loading && !prediction && !error && (
                                    <div
                                        className="h-full flex flex-col items-center justify-center text-center min-h-[300px] opacity-40">
                                        <FileImage className="w-16 h-16 mb-4 text-gray-300"/>
                                        <p className="text-lg">Click "Generate Article" to process this image.</p>
                                    </div>
                                )}

                                {!loading && prediction && (
                                    <div className="animate-in fade-in duration-500">
                                        <div className="prose prose-indigo max-w-none">
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{prediction}</ReactMarkdown>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}