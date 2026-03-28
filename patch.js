const fs = require('fs');
const content = fs.readFileSync('m:\\Projects\\MAJ FIN\\frontend\\index.html', 'utf8');

const replacement = `            // Map Partition Tags evenly mapped
            partitions: {
                "Entry": { x: 300, y: 360 },${(() => {
        const aisles = [
            { id: 1, x: 100, w: 60, y: 50, h: 250 },
            { id: 2, x: 250, w: 60, y: 50, h: 250 },
            { id: 3, x: 400, w: 60, y: 50, h: 250 }
        ];
        let s = '\\n';
        aisles.forEach(a => {
            for (let i = 1; i <= 6; i++) {
                const y_o = (i - 0.5) * (a.h / 6);
                const xx = a.x + a.w / 2;
                const yy = a.y + y_o;
                s += \`                "Aisle ${a.id} - P10${i}": { x: \${xx}, y: \${yy} },\\n\`;
                            s += \`                "P10${i}": { x: \${xx}, y: \${yy} },\\n\`;
                        }
                    });
                    return s;
                })()}            }
        };`;

                // replace up to mapConfig end natively!
                const re = /partitions:\s*\{[\s\S]*?\};\s*(?=function openNavModal)/;

                const newText = content.replace(re, replacement + '\n\n        ');

                fs.writeFileSync('m:\\Projects\\MAJ FIN\\frontend\\index.html', newText);
                console.log('Successfully JS string replaced config!');
