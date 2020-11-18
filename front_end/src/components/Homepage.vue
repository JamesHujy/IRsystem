
<template>
    <div>
        <vue-canvas-nest :config = "{color: '51,102,204', count: 219, opacity:1}"></vue-canvas-nest>
        <center id = "searchEngine">
            <h1>ChiEasy搜索引擎</h1>
            <div v-for='item in itemList' :key="item" style="margin-bottom:15px">
            
            <el-row gutter="10">
                <el-col span="1" offset="4"><el-button icon="el-icon-close" circle type="info" v-on:click="deleteWord(item)"></el-button></el-col>
                <el-col span="4" offset="-2"><el-input placeholder="请输入内容" style="width:200px" v-model="item.word" @blur="submitPosGet(item)"></el-input></el-col>
                <el-col span="4">
                    <el-select v-model="item.pos" placeholder="POS" style="width:150px">
                        <el-option
                            v-for="choice in item.posList"
                            :key="choice"
                            :label="choice"
                            :value="choice">
                        </el-option>
                </el-select>
                </el-col>
                <el-col span="4">
                    <el-select v-model="item.relative" placeholder="位置关系" style="width:150px">
                        <el-option
                            v-for="choice in relativeList"
                            :key="choice"
                            :label="choice"
                            :value="choice">
                        </el-option>
                    </el-select>
                </el-col>
                <el-col span="4">
                    <el-select v-model="item.relativeObject" placeholder="相对于..." style="width:150px">
                        <el-option
                            v-for="choice in item.relativeOptions"
                            :key="choice"
                            :label="choice"
                            :value="choice">
                        </el-option>
                    </el-select>
                </el-col>
            </el-row>
            </div>
            <div style="margin-bottom:25px">
            <el-row gutter="10">
            <el-col :span="6" offset="6"><el-button v-on:click="addWord">添加</el-button></el-col>
            <el-col :span="3" offset="-6"><el-button type="primary" icon="el-icon-search" v-on:click="sumbitQuery">搜索</el-button></el-col>
            </el-row>
            </div>
            <div class="source">
                <div>
                    <ul class="infinite-list"  v-if="sentenceList.length > 0" v-infinite-scroll="load" infinite-scroll-disabled="disabled" style="overflow:auto">
                        <li v-for="sen in showsenList" :key="sen" class="infinite-list-item" >{{ sen }}</li>
                    </ul>
                </div>
            </div>
        </center>
    </div>
</template>


<script src="dist/canvas-nest.js"></script>

<script>

import vueCanvasNest from 'vue-canvas-nest';
import axios from "axios";
import Qs from 'qs';
export default {
	name: 'SearchHome',
    components: {
        vueCanvasNest
    },
	data (){
        return {
            count:1,
            itemList:[
                {id:1, word:"", pos:"不限", posList:['不限','名词', '人名', '地名', '机构名', '其它专名', '数词', '量词', '数量词', '时间词', '方位词', '处所词', '动词', '形容词', '副词', '前接成分', '后接成分', '习语', '简称', '代词', '连词', '介词', '助词', '语气助词', '叹词', '拟声词', '语素', '标点', '其它'], 
                 relative: '不限', relativeObject:"", relativeOptions:[]}
            ],
            wordList: [],
            relativeList: ['不限', '左相邻', '靠左', '靠右', '右相邻'],
            sentenceList: [],
            showsenList: [],
            scrollCount: 1,
            loading: false
        }
	},
	methods: {
        addWord: function() {
            this.itemList.push({id:this.count, word:"", pos:"不限", posList:['不限','名词', '人名', '地名', '机构名', '其它专名', '数词', '量词', '数量词', '时间词', '方位词', '处所词', '动词', '形容词', '副词', '前接成分', '后接成分', '习语', '简称', '代词', '连词', '介词', '助词', '语气助词', '叹词', '拟声词', '语素', '标点', '其它'], 
                                relative: "不限", relativeObject:"", relativeOptions:[]});
            this.count = this.count + 1
        },
        deleteWord: function(item) {
            this.itemList.splice(this.itemList.indexOf(item), 1)
        },
        submitPosGet: function(item) {
            const path = "http://166.111.121.32:12306/get"
            axios.get(path, {params:{'words': item.word, 'type':'1'}}
            ).then((response) => {
                item.posList = ['不限'].concat(response.data)
            })
            .catch(error => {
                error
            })
            var notEmptyList = []
            for (var i = 0, len=this.itemList.length; i < len; i++) {
                if (this.itemList[i].word != "") {
                    notEmptyList.push(this.itemList[i].word)
                }
            }

            for (var i = 0, len=this.itemList.length; i < len; i++) {
                this.itemList[i].relativeOptions = []
                for (var j = 0, len2=notEmptyList.length; j < len2; j++) {
                    if (notEmptyList[j] != this.itemList[i].word) {
                        this.itemList[i].relativeOptions.push(notEmptyList[j])
                    }
                }
            }
        },
        load: function(){
            this.laoding = true
            this.scrollCount += 2
            this.showsenList = this.sentenceList.slice(0,this.scrollCount)
        },
        sumbitQuery: function() {
            const path = "http://166.111.121.32:12306/get"
            let wordsList = []
            let posList = []
            let relative = []
            let relativeObject = []
            console.log(this.itemList.length)
            for(var i=0;i<this.itemList.length;i++){
                wordsList.push(this.itemList[i].word)
                posList.push(this.itemList[i].pos)
                relative.push(this.itemList[i].relative)
                relativeObject.push(this.itemList[i].relativeObject)
            }
            axios.get(path, {params:{'words': wordsList.join(), 'type':'2', 'posList': posList.join(), 'relative':relative.join(), 'relativeObject':relativeObject.join()}}
            ).then((response) => {
                this.sentenceList = response.data
                this.loading = false
                this.showsenList = this.sentenceList
            })
            .catch(error => {
                error
            })
        }
	},
    computed: {
        noMore() {
            //当起始页数大于总页数时停止加载
        return this.scrollCount >= this.sentenceList.length - 1;
        },
        disabled() {
            return this.loading || this.noMore;
        }
    }
}

</script>


<style scoped>
#searchEngine {
    top: 5%;
    width: 100%;
    position: fixed;
    background-color: transparent;
    z-index: 1;
}

#searchEngine h1 {
    font-size: 50px;
}

#text {
    width: 40%;
    height: 41px;
    padding: 0px;
    margin:-1px 0 0 0px;
    border: solid 1px #39F;
    font-size:24px; 
}

.source {
    padding: 24px;
    max-height: 80px;
    width: 60%;
}
.infinite-list {
    height: 450px;
    padding: 0;
    margin: 0;
    list-style: none;
}
.infinite-list .infinite-list-item {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 50px;
    background: #e8f3fe;
    margin: 10px;
    color: #7dbcfc;
}

</style>