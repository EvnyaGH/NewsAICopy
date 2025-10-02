// src/pages/InterestsSettings.jsx
import { useEffect, useMemo, useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { api } from '@/services/api';

export default function InterestsSettings() {
    const [fields, setFields] = useState([]);
    const [selectedFields, setSelectedFields] = useState([]);
    const [selectedTopics, setSelectedTopics] = useState([]);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        api.getFields().then(res => setFields(res.data?.data || []));
        api.getInterests().then(res => {
            const d = res.data?.data || {};
            setSelectedFields(d.fields || []);
            setSelectedTopics(d.subtopics || []);
        });
    }, []);

    const grouped = useMemo(() => fields, [fields]);
    const toggle = (arr, setArr, v) =>
        setArr(prev => prev.includes(v) ? prev.filter(x => x !== v) : [...prev, v]);

    const save = async () => {
        setSaving(true);
        try {
            await api.updateInterests({ fields: selectedFields, subtopics: selectedTopics });
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto px-4 space-y-6">
            <Helmet><title>Interests Settings</title></Helmet>
            <h1 className="text-2xl font-semibold">Interests</h1>

            <div className="grid md:grid-cols-3 gap-8">
                {grouped.map(group => (
                    <div key={group.slug} className="space-y-2">
                        <div className="font-semibold">{group.name}</div>
                        <div className="space-y-2">
                            {(group.subtopics || []).map(t => (
                                <label key={t} className="flex items-center gap-2 text-sm">
                                    <input
                                        type="checkbox"
                                        checked={selectedTopics.includes(t)}
                                        onChange={() => toggle(selectedTopics, setSelectedTopics, t)}
                                    />
                                    {t}
                                </label>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            <div className="flex gap-3">
                <button onClick={save} disabled={saving} className="px-3 py-2 rounded bg-black text-white">
                    {saving ? 'Saving…' : 'Save Interests'}
                </button>
                <button
                    className="px-3 py-2 rounded border"
                    onClick={() => { setSelectedFields([]); setSelectedTopics([]); }}
                >
                    Clear Interests
                </button>
            </div>
        </div>
    );
}
